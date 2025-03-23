import json
import http.cookies
from enum import Enum
from abc import ABC, abstractmethod

class HttpStatus(Enum):
    OK = (200, "OK")
    CREATED = (201, "Created")
    NO_CONTENT = (204, "No Content")
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    FOUND = (302, "Found")

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



class IResponse(ABC):
    """Interface para respostas HTTP"""

    def __init__(self, status: HttpStatus, content_type: str, headers=None, cookies=None):
        self.status = status
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.content_type = content_type

        # # Define o Content-Type automaticamente
        # self.headers.setdefault("Content-Type", f"{self.content_type}; charset=utf-8")

    @abstractmethod
    def to_response(self) -> str:
        """Método abstrato para gerar a resposta HTTP"""
        pass


class JsonResponse(IResponse):
    """Resposta no formato JSON"""

    def __init__(self, status: HttpStatus= HttpStatus.OK, data=None, headers=None, cookies=None):
        super().__init__(status, "application/json", headers, cookies)
        self.body = data

    def to_response(self) -> Response:
        """Retorna um objeto Response formatado"""
        return Response(status= self.status, data= self.body, headers=self.headers, cookies=self.cookies,content_type=self.content_type)
    

class HtmlResponse(IResponse):
    """Resposta no formato HTML"""

    def __init__(self, status: HttpStatus, data="", headers=None, cookies=None):
        super().__init__(status, "text/html", headers, cookies)
        self.body = data

    def to_response(self) -> Response:
        """Retorna um objeto Response formatado"""
        return Response(status=self.status, data=self.body, headers=self.headers, cookies=self.cookies,content_type= self.content_type)


class RedirectResponse(IResponse):
    def __init__(self, location: str, status=HttpStatus.FOUND):
        self.location = location
        self.status = status

    def to_response(self):
        return Response(self.status, headers={"Location": self.location})
