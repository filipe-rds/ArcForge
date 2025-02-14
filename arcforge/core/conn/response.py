

# aind n foi implementado, mas será necessário usar, pois éh um requisito

import json

class Response:
    def __init__(self,status=200 ,data=None, content_type="application/json", headers=None):
        self.status = status
        self.content_type = content_type
        self.body = data
        self.headers = headers if headers else {}

    def to_http_response(self):
        status_line = f"HTTP/1.1 {self.status} {self._get_status_message(self.status)}"
        headers = f"Content-Type: {self.content_type}\n"
        for key, value in self.headers.items():
            headers += f"{key}: {value}\n"

        return f"{status_line}\n{headers}\n{self.body}"
        # return f"HTTP/1.1 {self.status} OK\nContent-Type: {self.content_type}\n\n{self.body}"
    
    def _serialize_data(self, data):
        if data is None:
            return ""
        if self.content_type == "application/json":
            try:
                return json.dumps(data, default=self._default_serializer)
            except (TypeError, ValueError):
                raise ValueError("Erro ao serializar os dados em JSON.")
        return str(data)
    
    @staticmethod
    def _default_serializer(obj):
        if hasattr(obj, "__dict__"):  # Converte objetos com atributos em dicionários
            return obj.__dict__
        raise TypeError(f"Objeto {obj} não é serializável em JSON.")
    
    @staticmethod
    def _get_status_message(status):
        status_messages = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
        }
        return status_messages.get(status, "Unknown Status")


