# Modelo Exemplo
print("entrou aqui 1")
from base_model import BaseModel, Field


class UserRR(BaseModel):
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
UserRR.set_conexao()
UserRR.create_table()
new_user = UserRR(codigoid = 4022222024,name="Aleeeice", email="alieeeeeeecewqqwewqddddde@eeexaeeemple.com")
new_user.save()

Escola.create_table()
new_user1 = Escola(codigoid = 4022222024,name="Aleeeice", email="alieeeeeeecewqqwewqddddde@eeexaeeemple.com")
new_user1.save()




# Consultar Dados
# users = UserRR.filter(name="Alice")
# print(users)
