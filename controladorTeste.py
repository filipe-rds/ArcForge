from arcforge.core.db.connection import DatabaseConnection
from arcforge.core.model.model import Model
from arcforge.core.model.field import IntegerField, CharField

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


