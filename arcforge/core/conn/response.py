

# aind n foi implementado, mas será necessário usar, pois éh um requisito

import json

class Response:
    def __init__(self,status=200 ,data=None, content_type="application/json", headers=None):
        self.status = status
        self.content_type = content_type
        self.body = json.dumps(data)
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
                return json.dumps(data)
            except (TypeError, ValueError):
                raise ValueError("Erro ao serializar os dados em JSON.")
        return str(data)
    
    @staticmethod
    def _get_status_message(status):
        """Retorna a mensagem padrão para o código de status HTTP."""
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



# Testando a resposta
dados = {"mensagem": "Olá, Gabriel!", "sucesso": True}
resposta = Response(status=201,data=dados)
print(resposta.to_http_response())
