from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs

class Request:
    """
    Classe responsável por armazenar os dados da requisição HTTP.
    """
    def __init__(self, handler):
        self.method = handler.command
        self.path = handler.path
        self.headers = handler.headers
        self.cookies = self._parse_cookies()
        self.body = self._parse_body(handler)
        self.form = self.body if isinstance(self.body, dict) else {}

    def _parse_cookies(self):
        """Converte os cookies da requisição em um dicionário."""
        cookie = SimpleCookie(self.headers.get("Cookie"))
        return {key: morsel.value for key, morsel in cookie.items()}

    def _parse_body(self, handler):
        """Lê e interpreta o corpo da requisição como JSON ou form-urlencoded."""
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length > 0:
            raw_body = handler.rfile.read(content_length).decode('utf-8')
            content_type = self.headers.get("Content-Type", "")

            if "application/json" in content_type:
                try:
                    return json.loads(raw_body)  # Requisições JSON
                except json.JSONDecodeError:
                    return {}

            elif "application/x-www-form-urlencoded" in content_type:
                return {k: v[0] for k, v in parse_qs(raw_body).items()}  # Formulário HTML

        return {}
