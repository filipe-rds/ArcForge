from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
import json


class Request:
    """
    Classe responsável por armazenar os dados da requisição HTTP.
    """
    def __init__(self, handler: BaseHTTPRequestHandler):
        self.method = handler.command
        self.path = handler.path
        self.headers = handler.headers
        self.cookies = self._parse_cookies()
        self.body = self._parse_body(handler)

    def _parse_cookies(self):
        """Converte os cookies da requisição em um dicionário."""
        cookie = SimpleCookie(self.headers.get("Cookie"))
        return {key: morsel.value for key, morsel in cookie.items()}

    def _parse_body(self, handler):
        """Lê e interpreta o corpo da requisição como JSON."""
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length > 0:
            raw_body = handler.rfile.read(content_length).decode('utf-8')
            try:
                return json.loads(raw_body)
            except json.JSONDecodeError:
                return {}
        return {}