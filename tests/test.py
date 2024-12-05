# from arcforge.core.model.base_model import *

#from arcforge.core.model.base_model import *

# class User(BaseModel):
#     _table_name = "departamento"
#     id = Field("SERIAL", primary_key=True)
#     name = Field("VARCHAR", nullable=False)
#     email = Field("VARCHAR", unique=True, nullable=False)


# class Escola(BaseModel):
#     _table_name = "setor"
#     id = Field("SERIAL", primary_key=True)
#     name = Field("VARCHAR", nullable=False)
#     email = Field("VARCHAR", unique=True, nullable=False)


# # Conectar e Criar Tabela
# User.set_conexao()
# User.create_table()
# new_user = User(codigoid = 4022222024,name="Alice", email="alieeeeeeecewqqwewqddddde@eeexaeeemple.com")
# new_user.save()

# Escola.create_table()
# new_user1 = Escola(codigoid = 4022222024,name="Alice", email="alieeeeeeecewqqwewqddddde@eeexaeeemple.com")
# new_user1.save()




# # Consultar Dados
# users = User.filter(name="Alice")
# print(users)


from arcforge.core.model.model import *
from arcforge.core.db.db_connection import *



# class Aluno(BaseModel):
#     _table_name = "aluno"
#     id = Field("SERIAL", primary_key=True)
#     nome = Field("VARCHAR")
#     idade = Field("INTEGER")


# class Escola(BaseModel):
#     _table_name = "escola"
#     id = Field("SERIAL", primary_key=True)
#     nome = Field("VARCHAR")
#     endereco = Field("VARCHAR")

# Cria uma instância de conexão com o banco de dados

# print("entrou aqui")
# # Cria as tabelas de Aluno e Escola
# db_connection.create_table(Aluno)
# print("criou aluno")
# db_connection.create_table(Escola)
# print("criou escola")

# Cria uma instância de Aluno
# aluno = Aluno(nome="Gabriel", idade=25)
# db_connection.save(aluno)




db_connection = DatabaseConnection()  

class Universidade(Model):
    _table_name = "universidade"
    id = Field("SERIAL", primary_key=True)
    nome = Field("VARCHAR")
    endereco = Field("VARCHAR")
    

class Aluno(Model):
    _table_name = "aluno"
    id = Field("SERIAL", primary_key=True)
    nome = Field("VARCHAR")
    idade = Field("INTEGER")
    #universidade = Field("INTEGER", foreign_key="universidade(id)")
    universidade = OneToMany(Universidade, on_delete="CASCADE")

db_connection.create_table(Universidade)
db_connection.create_table(Aluno)

u = Universidade(nome="UFSCddderrd", endereco="Florianqeqóddddpolis")
u = Universidade(nome="UFSCwqwqewqeddddd", endereco="Florianóddddpolqweqiddds")
u = Universidade(nome="UFSCdddwwwwdd", endereco="Floriawwwwnóddddpoliddds")
db_connection.save(u)
al = Aluno(nome="GabrielF", idade=25, universidade = 1)
al = Aluno(nome="GabrielA", idade=25, universidade = 2)
al = Aluno(nome="GabrielE", idade=25, universidade = 3)
db_connection.save(al)


