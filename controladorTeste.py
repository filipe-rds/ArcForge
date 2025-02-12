from arcforge.core.db.connection import DatabaseConnection
from arcforge.core.model.model import Model
from arcforge.core.model.field import IntegerField, CharField
from arcforge.core.conn.handler import RouteHandler

db = DatabaseConnection()


class Cliente(Model):
    _table_name = "cliente"
    id = IntegerField(primary_key=True)
    nome = CharField(max_length=100)
    email = CharField(max_length=100)

def clientes():
    clientes = db.query(Cliente)
    clientes_data = [cliente.to_dict() for cliente in clientes]
    return {
        "clientes": clientes_data
    }

#Funcionando

# Exemplo de uso:

def handle_get(handler):
    """Exemplo de função para lidar com requisições GET."""
    data = {"message": "Requisição GET bem-sucedida!"}
    handler._serve_json(data)

def handle_post(handler):
    """Exemplo de função para lidar com requisições POST."""
    content_length = int(handler.headers.get('Content-Length', 0))
    post_data = handler.rfile.read(content_length).decode("utf-8")
    response_data = {"message": "Dados recebidos com sucesso", "data": post_data}
    handler._serve_json(response_data)

# Registro de rotas
RouteHandler.add_route("/exemplo", methods={"GET": handle_get, "POST": handle_post})

