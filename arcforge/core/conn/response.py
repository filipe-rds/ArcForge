from enum import Enum
import json
import http.cookies

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
    

# -----------------------------------------------------------------------------
# Design Pattern: Builder
# A classe Response utiliza o padrão Builder para construir uma resposta HTTP de
# forma estruturada e passo a passo. Esse padrão é ideal para objetos complexos,
# como uma resposta HTTP, que envolve múltiplos componentes (status, headers,
# corpo da resposta e cookies).
# -----------------------------------------------------------------------------

class Response:
    def __init__(self, status: HttpStatus, data=None, cookies=None):
        self.status = status.code
        self.status_message = status.message
        self.cookies = cookies or {}
        self.body = self._serialize(data)
        self.headers = self._build_headers()
        

    def _serialize(self, data) -> str:
        if data is None:
            return ""
        if isinstance(data, (dict, list)):
            try:
                return json.dumps(data, default=self._default_serializer, indent=4, ensure_ascii=False)
            except Exception as e:
                raise ValueError("Erro ao serializar os dados para JSON.") from e
        if isinstance(data, str):
            return data
        try:
            return json.dumps(data, default=self._default_serializer, indent=4, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Erro ao serializar o objeto {type(data).__name__} para JSON.") from e

    def _default_serializer(self, obj):
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        raise TypeError(f"Objeto do tipo {type(obj).__name__} não é serializável")

    def _build_headers(self) -> dict:
        headers = {}
        if self.body:
            body_strip = self.body.lstrip()
            if body_strip.startswith("{") or body_strip.startswith("["):
                headers["Content-Type"] = "application/json; charset=utf-8"
            else:
                headers["Content-Type"] = "text/plain; charset=utf-8"
            headers["Content-Length"] = str(len(self.body.encode("utf-8")))
        else:
            headers["Content-Type"] = "text/plain; charset=utf-8"
        
        # Adiciona os cookies ao cabeçalho apenas se existirem.
        if self.cookies:  # Só inclui "Set-Cookie" se houver cookies
            cookies = self._build_cookies()
            headers["Set-Cookie"] = cookies
        return headers

    def _build_cookies(self) -> str:
        cookie_str = []
        for key, value in self.cookies.items():
            cookie = http.cookies.SimpleCookie()
            # Converte o valor para string explicitamente
            cookie[key] = str(value)
            cookie_str.append(cookie.output(header="", sep="").strip())
        return "; ".join(cookie_str)

    def to_http_response(self) -> str:
        status_line = f"HTTP/1.1 {self.status} {self.status_message}"
        headers_lines = "\r\n".join(f"{key}: {value}" for key, value in self.headers.items())
        return f"{status_line}\r\n{headers_lines}\r\n\r\n{self.body}"

__all__ = ["Response", "HttpStatus"]