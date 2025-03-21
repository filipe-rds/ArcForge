import json
import http.cookies
from enum import Enum

class HttpStatus(Enum):
    OK = (200, "OK")
    CREATED = (201, "Created")
    NO_CONTENT = (204, "No Content")
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f"{self.code} {self.message}"

class JsonSerializer:
    """Responsável por serializar objetos para JSON."""
    @staticmethod
    def serialize(data) -> str:
        if data is None:
            return ""
        if isinstance(data, (dict, list, str)):
            return json.dumps(data, indent=4, ensure_ascii=False)
        if hasattr(data, "__dict__"):
            return json.dumps(data.__dict__, indent=4, ensure_ascii=False)
        raise TypeError(f"Objeto do tipo {type(data).__name__} não é serializável")

class Response:
    def __init__(self, status: HttpStatus, data=None, headers=None, cookies=None, content_type="application/json"):
        self.status = status.code
        self.status_message = status.message
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.content_type = content_type

        if content_type == "text/html":
            self.body = data if isinstance(data, str) else ""
            self.headers.setdefault("Content-Type", "text/html; charset=utf-8")
        else:
            self.body = JsonSerializer.serialize(data)
            self.headers.setdefault("Content-Type", "application/json; charset=utf-8")

        self._set_default_headers()

    def _set_default_headers(self):
        """Define os headers padrão da resposta."""
        if self.body:
            self.headers.setdefault("Content-Type", "application/json; charset=utf-8")
            self.headers.setdefault("Content-Length", str(len(self.body.encode("utf-8"))))
        else:
            self.headers.setdefault("Content-Type", "text/plain; charset=utf-8")

        # Adiciona cookies, se houver
        if self.cookies:
            self.headers["Set-Cookie"] = self._build_cookies()

    def _build_cookies(self) -> str:
        """Gera a string de cookies para o cabeçalho HTTP."""
        return "; ".join(f"{key}={value}" for key, value in self.cookies.items())

    def to_http_response(self) -> str:
        """Retorna a resposta HTTP formatada."""
        status_line = f"HTTP/1.1 {self.status} {self.status_message}"
        headers_lines = "\r\n".join(f"{key}: {value}" for key, value in self.headers.items())
        return f"{status_line}\r\n{headers_lines}\r\n\r\n{self.body}"
