# Modelo Exemplo
print("entrou aqui 1")
from arcforge.core.model import BaseModel, Field


class User(BaseModel):
    _table_name = "departamento"
    id = Field("SERIAL", primary_key=True)
    name = Field("VARCHAR", nullable=False)
    email = Field("VARCHAR", unique=True, nullable=False)


class Escola(BaseModel):
    _table_name = "setor"
    id = Field("SERIAL", primary_key=True)
    name = Field("VARCHAR", nullable=False)
    email = Field("VARCHAR", unique=True, nullable=False)


# Conectar e Criar Tabela
User.set_conexao()
User.create_table()
new_user = User(codigoid = 4022222024,name="Alice", email="alieeeeeeecewqqwewqddddde@eeexaeeemple.com")
new_user.save()

Escola.create_table()
new_user1 = Escola(codigoid = 4022222024,name="Alice", email="alieeeeeeecewqqwewqddddde@eeexaeeemple.com")
new_user1.save()




# Consultar Dados
users = User.filter(name="Alice")
print(users)
