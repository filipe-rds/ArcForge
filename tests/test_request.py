from arcforge.core.db.connection import DatabaseConnection
from arcforge.core.model.model import Model
from arcforge.core.model.field import IntegerField, CharField
from arcforge.core.conn.handler import RouteHandler
from arcforge.core.conn.server import WebServer
from arcforge.core.conn.response import Response
from arcforge.core.conn.controller import Controller
import json

# Inicializa a conexão com o banco
db = DatabaseConnection()

class Cliente(Model):
    _table_name = "cliente"
    id = IntegerField(primary_key=True)
    nome = CharField(max_length=100)
    email = CharField(max_length=100)

# Configuração do banco
def setup_database():
    db.create_table(Cliente)
    db.save(Cliente(nome="João Silva", email="joao@email.com"))
    db.save(Cliente(nome="Maria Souza", email="maria@email.com"))

# Controlador para Cliente
class ClienteController(Controller):
    @RouteHandler.route("/clientes", "GET")
    def get_clientes(handler):
        clientes = db.find_all(Cliente)
        if clientes:
            return Response(200, clientes)
        return Response(404, {"error": "Nenhum cliente encontrado"})

    @RouteHandler.route("/clientes/{id}", "GET")
    def get_cliente(handler, id):
        cliente = db.read(Cliente, id)
        if cliente:
            return Response(200, cliente)
        return Response(404, {"error": "Cliente não encontrado"})

    @RouteHandler.route("/clientes", "POST")
    def create_cliente(handler, body):  # O `body` já chega pronto como dicionário
        cliente = Cliente(**body)  # Constrói diretamente
        db.save(cliente)
        return Response(201, cliente)

    @RouteHandler.route("/clientes/{id}", "PUT")
    def update_cliente(handler, body, id):  # Agora também aceita updates diretos
        cliente = db.read(Cliente, id)
        if not cliente:
            return Response(404, {"error": "Cliente não encontrado"})

        for key, value in body.items():
            setattr(cliente, key, value)  # Atualiza dinamicamente os atributos
        db.save(cliente)
        return Response(200, cliente)


if __name__ == "__main__":
    setup_database()
    ClienteController()  # Instancia o controlador para registrar as rotas automaticamente
    WebServer(port=8080)