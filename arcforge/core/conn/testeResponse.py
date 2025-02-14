
from response import Response


# Testando a resposta
dados = {"mensagem": "Olá, Gabriel!", "sucesso": True}
resposta = Response(status=201,data=dados)
print("primeira resposta")
print(resposta.to_http_response())
print("segunda resposta")


print('-----------------------------------------------')

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

# Lista de objetos User
users = [User(1, "Alice"), User(2, "Bob")]

res = Response(status=200,data=users)

#print(res.to_http_response())

print(res.body)
print(res.content_type)
print(res.headers)
print(res.status)


print('-----------------------------------------------')










Lucas = User(3,"Lucas")

ola = Response(status=200,data=Lucas)

print(ola.to_http_response())