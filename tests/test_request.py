from arcforge.core.db.connection import DatabaseConnection
from arcforge.core.model.model import Model
from arcforge.core.model.field import IntegerField, CharField
from arcforge.core.model.relationships import ManyToOne
from arcforge.core.conn.handler import RouteHandler
from arcforge.core.conn.server import WebServer
from arcforge.core.conn.response import Response
import json

db = DatabaseConnection()

class Cliente(Model):
    _table_name = "cliente"
    id = IntegerField(primary_key=True)
    nome = CharField(max_length=100)
    email = CharField(max_length=100)

def setup_database():
    """Cria as tabelas necessárias para os testes."""
    db.create_table(Cliente)

def test_insert_clientes():
    cliente1 = db.save(Cliente(nome="João Silva", email="joao@email.com"))
    cliente2 = db.save(Cliente(nome="Maria Souza", email="maria@email.com"))
    return cliente1, cliente2

def get_cliente():
    clientes = db.find_all(Cliente)

def controller_GET_clientes(handler):
    clientes = db.find_all(Cliente)
    res = Response(status=200,data= clientes)
    if clientes:
        handler._serve_json(res)
    else:
        handler._not_found()

def controller_GET_cliente(handler,id):
    cliente = db.read(Cliente,id)
    res = Response(status=200,data=cliente)
    if cliente:
        handler._serve_json(res)
    else:
        handler._not_found()

def controller_POST_cliente(handler, novo_cliente_json):
    # Caso 'novo_cliente_json' seja uma string JSON, converta para dicionário
    if isinstance(novo_cliente_json, str):
        novo_cliente = json.loads(novo_cliente_json)
    else:
        novo_cliente = novo_cliente_json

    # Cria a instância do cliente usando desempacotamento
    cliente = Cliente(**novo_cliente)
    
    # Salva o cliente no banco de dados
    db.save(cliente)
    
    # Prepara a resposta (por exemplo, retornando os dados do cliente criado)
    res = Response(status=201, data=cliente)
    handler._serve_json(res)


if __name__ == "__main__":

    setup_database()

    RouteHandler.add_route("/clientes",methods={"GET":controller_GET_clientes})
    RouteHandler.add_route("/clientes",methods={"POST":controller_POST_cliente})
    RouteHandler.add_route("/clientes/{id}",methods={"GET":controller_GET_cliente})

    WebServer.start(port=9090)  


