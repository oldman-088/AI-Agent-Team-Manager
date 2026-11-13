import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

from team_manager.app import handler_for, initialize


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.temp.name) / 'test.sqlite3')
        initialize(self.db)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(self.db))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, method, path, data=None, headers=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        headers = headers or {}
        if data is not None:
            headers.setdefault('Content-Type', 'application/json')
            data = json.dumps(data)
        connection.request(method, path, data, headers)
        response = connection.getresponse()
        content = response.read()
        connection.close()
        return response.status, json.loads(content) if response.getheader('Content-Type', '').startswith('application/json') else content

    def test_crud_and_persistence(self):
        status, agent = self.request('POST', '/api/agents', {'name': 'Ada', 'role': 'Engineer'})
        self.assertEqual(status, 201)
        status, task = self.request('POST', '/api/tasks', {'title': 'Build', 'description': 'First', 'agent_id': agent['id']})
        self.assertEqual(status, 201)
        status, updated = self.request('PATCH', f"/api/tasks/{task['id']}", {'status': 'done'})
        self.assertEqual((status, updated['status']), (200, 'done'))
        initialize(self.db)  # reopening the database does not reset data
        self.assertEqual(len(self.request('GET', '/api/tasks')[1]), 1)
        self.assertEqual(self.request('DELETE', f"/api/agents/{agent['id']}", {})[0], 200)
        self.assertIsNone(self.request('GET', '/api/tasks')[1][0]['agent_id'])
        self.assertEqual(self.request('DELETE', f"/api/tasks/{task['id']}", {})[0], 200)
        self.assertEqual(self.request('GET', '/api/tasks')[1], [])

    def test_validation_and_origin(self):
        self.assertEqual(self.request('POST', '/api/agents', {'name': '', 'role': 'test'})[0], 400)
        self.assertEqual(self.request('POST', '/api/tasks', {'title': 'x', 'agent_id': 99})[0], 400)
        self.assertEqual(self.request('POST', '/api/tasks', {'title': 'x'}, {'Origin': 'https://evil.example'})[0], 400)
        self.assertEqual(self.request('PATCH', '/api/tasks/1', {'status': 'bad'})[0], 400)
        self.assertEqual(self.request('PATCH', '/api/tasks/1', {'title': 'bad'})[0], 400)
        self.assertEqual(self.request('DELETE', '/api/tasks/99', {})[0], 404)
        self.assertEqual(self.request('GET', '/../../README.md')[0], 404)
        self.assertEqual(self.request('GET', '/')[0], 200)


if __name__ == '__main__':
    unittest.main()
