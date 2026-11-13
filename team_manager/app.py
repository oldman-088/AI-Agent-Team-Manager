"""Dependency-free local HTTP API and SQLite persistence."""
import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
STATUSES = ('todo', 'in_progress', 'done')


def connect(path):
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db


def initialize(path):
    with connect(path) as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'todo' CHECK(status IN ('todo','in_progress','done')),
            agent_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        ''')


def text(value, field, limit, required=True):
    if not isinstance(value, str):
        raise ValueError(f'{field} must be a string')
    value = value.strip()
    if (required and not value) or len(value) > limit:
        raise ValueError(f'{field} must be {"1" if required else "0"}–{limit} characters')
    return value


def handler_for(db_path):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status, data):
            body = json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def body(self):
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if size <= 0 or size > 16384:
                    raise ValueError('Request body must be between 1 and 16384 bytes')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError('Expected a JSON object')
                return data
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise ValueError('Invalid JSON')

        def same_origin(self):
            # Browsers send Origin for cross-origin writes; reject those requests.
            origin = self.headers.get('Origin')
            if origin and (urlsplit(origin).netloc != self.headers.get('Host') or urlsplit(origin).scheme not in ('http', 'https')):
                raise ValueError('Cross-origin requests are not allowed')
            if self.headers.get('Sec-Fetch-Site') == 'cross-site':
                raise ValueError('Cross-origin requests are not allowed')
            if self.headers.get_content_type() != 'application/json':
                raise ValueError('Content-Type must be application/json')

        def do_GET(self):
            path = urlsplit(self.path).path
            if path in ('/api/agents', '/api/tasks'):
                table = path.rsplit('/', 1)[1]
                with connect(db_path) as db:
                    rows = db.execute(f'SELECT * FROM {table} ORDER BY id DESC').fetchall()
                return self.send_json(200, [dict(row) for row in rows])
            files = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8')}
            if path not in files:
                return self.send_json(404, {'error': 'Not found'})
            name, content_type = files[path]
            content = (ROOT / 'static' / name).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'self'")
            self.end_headers()
            self.wfile.write(content)

        def do_POST(self):
            self.mutate('POST')

        def do_PATCH(self):
            self.mutate('PATCH')

        def do_DELETE(self):
            self.mutate('DELETE')

        def mutate(self, method):
            try:
                self.same_origin()
                parts = urlsplit(self.path).path.strip('/').split('/')
                if len(parts) not in (2, 3) or parts[0] != 'api' or parts[1] not in ('agents', 'tasks'):
                    return self.send_json(404, {'error': 'Not found'})
                table = parts[1]
                if method == 'POST' and len(parts) == 2:
                    data = self.body()
                    with connect(db_path) as db:
                        if table == 'agents':
                            cursor = db.execute('INSERT INTO agents(name, role) VALUES (?, ?)', (text(data.get('name'), 'name', 100), text(data.get('role'), 'role', 200)))
                        else:
                            agent_id = data.get('agent_id')
                            if agent_id is not None and (type(agent_id) is not int or agent_id <= 0):
                                raise ValueError('agent_id must be a positive integer or null')
                            cursor = db.execute('INSERT INTO tasks(title, description, agent_id) VALUES (?, ?, ?)', (text(data.get('title'), 'title', 200), text(data.get('description', ''), 'description', 4000, False), agent_id))
                        row = db.execute(f'SELECT * FROM {table} WHERE id = ?', (cursor.lastrowid,)).fetchone()
                    return self.send_json(201, dict(row))
                if len(parts) != 3 or not parts[2].isdigit() or int(parts[2]) < 1:
                    return self.send_json(404, {'error': 'Not found'})
                item_id = int(parts[2])
                with connect(db_path) as db:
                    if method == 'DELETE':
                        cursor = db.execute(f'DELETE FROM {table} WHERE id = ?', (item_id,))
                    elif method == 'PATCH' and table == 'tasks':
                        data = self.body()
                        if not data or set(data) - {'status', 'agent_id'}:
                            raise ValueError('Only status and agent_id can be updated')
                        if 'status' in data and data['status'] not in STATUSES:
                            raise ValueError('Invalid status')
                        if 'agent_id' in data and data['agent_id'] is not None and (type(data['agent_id']) is not int or data['agent_id'] <= 0):
                            raise ValueError('agent_id must be a positive integer or null')
                        columns = ', '.join(f'{key} = ?' for key in data)
                        cursor = db.execute(f'UPDATE tasks SET {columns} WHERE id = ?', (*data.values(), item_id))
                    else:
                        return self.send_json(404, {'error': 'Not found'})
                    if not cursor.rowcount:
                        return self.send_json(404, {'error': 'Not found'})
                    row = db.execute(f'SELECT * FROM {table} WHERE id = ?', (item_id,)).fetchone() if method == 'PATCH' else None
                return self.send_json(200, dict(row) if row else {'deleted': True})
            except (ValueError, sqlite3.IntegrityError) as exc:
                self.send_json(400, {'error': 'Invalid agent reference' if isinstance(exc, sqlite3.IntegrityError) else str(exc)})

    return Handler


def main():
    parser = argparse.ArgumentParser(description='Run the local team manager')
    parser.add_argument('--host', default='127.0.0.1', help='Bind address (default: loopback)')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--db', default='team_manager.sqlite3')
    args = parser.parse_args()
    initialize(args.db)
    server = ThreadingHTTPServer((args.host, args.port), handler_for(args.db))
    print(f'Serving on http://{args.host}:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
