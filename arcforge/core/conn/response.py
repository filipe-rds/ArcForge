

# aind n foi implementado, mas será necessário usar, pois éh um requisito

import json

class Response:
    def __init__(self, data, content_type="application/json"):
        #self.status = status
        self.content_type = content_type
        self.body = json.dumps(data)

    def to_http_response(self):
        return f"HTTP/1.1 {self.status} OK\nContent-Type: {self.content_type}\n\n{self.body}"

# Testando a resposta
dados = {"mensagem": "Olá, Gabriel!", "sucesso": True}
resposta = Response(dados)
print(resposta.to_http_response())
