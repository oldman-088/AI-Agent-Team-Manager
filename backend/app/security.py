"""Local host/origin guard and optional shared bearer gate.

A shared token is not per-user identity or role-based authorization.
"""
from secrets import compare_digest
from urllib.parse import urlsplit
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class LocalGuard(BaseHTTPMiddleware):
    def __init__(self, app, api_token: str | None = None):
        super().__init__(app)
        self._token = api_token.encode('ascii') if api_token else None

    async def dispatch(self, request: Request, call_next):
        host = request.headers.get('host', '')
        # Restrict browser DNS rebinding and accidental public exposure. Localhost only.
        try:
            parsed = urlsplit(f'http://{host}')
            if parsed.hostname not in ('localhost', '127.0.0.1', '::1') or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
                return JSONResponse({'detail': 'Invalid host'}, status_code=403)
            _ = parsed.port  # validate port syntax
        except ValueError:
            return JSONResponse({'detail': 'Invalid host'}, status_code=403)
        # Optional shared bearer gate; local host/origin checks remain mandatory.
        if self._token and (request.url.path == '/api' or request.url.path.startswith('/api/')):
            authorization = request.headers.get('authorization', '')
            scheme, separator, credential = authorization.partition(' ')
            valid = separator and scheme.lower() == 'bearer' and compare_digest(credential.encode('utf-8'), self._token)
            if not valid:
                return JSONResponse({'detail': 'Authentication required'}, status_code=401,
                                    headers={'WWW-Authenticate': 'Bearer', 'Cache-Control': 'no-store'})
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            origin = request.headers.get('origin')
            if origin:
                try:
                    parsed_origin = urlsplit(origin)
                    if parsed_origin.scheme not in ('http', 'https') or parsed_origin.netloc != host or parsed_origin.path or parsed_origin.query or parsed_origin.fragment:
                        return JSONResponse({'detail': 'Invalid origin'}, status_code=403)
                except ValueError:
                    return JSONResponse({'detail': 'Invalid origin'}, status_code=403)
            if request.headers.get('sec-fetch-site') == 'cross-site':
                return JSONResponse({'detail': 'Cross-site request rejected'}, status_code=403)
            if request.method in ('POST', 'PUT', 'PATCH') and request.headers.get('content-type', '').split(';', 1)[0].strip().lower() != 'application/json':
                return JSONResponse({'detail': 'JSON content type required'}, status_code=415)
        response = await call_next(request)
        if request.url.path == '/api' or request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        return response
