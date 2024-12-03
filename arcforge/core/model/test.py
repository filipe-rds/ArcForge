# Modelo Exemplo
print("entrou aqui 1")
from base_model import BaseModel, Field


class UserRR(BaseModel):
    _table_name = "departamento"
    id = Field("SERIAL", primary_key=True)
    name = Field("VARCHAR", nullable=False)
    email = Field("VARCHAR", unique=False, nullable=False)


class Escola(BaseModel):
    _table_name = "setor"
    id = Field("SERIAL", primary_key=True)
    name = Field("VARCHAR", nullable=False)
    email = Field("VARCHAR", unique=False, nullable=False)


# Conectar e Criar Tabela
UserRR.set_conexao()
UserRR.create_table()
new_user = UserRR(name="Alce", email="e@eeddeeeeeemple.com")
new_user.save()

Escola.create_table()
new_user1 = Escola(name="Aleeeice", email="alieweweweeemple.com")
new_user1.save()




# Consultar Dados
# users = UserRR.filter(name="Alice")
# print(users)
