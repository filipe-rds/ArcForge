from arcforge.core.model.model import *
from arcforge.core.db.db_connection import *

db_connection = DatabaseConnection()  

class Aluno(Model):
    _table_name = "aluno"
    id = Field("SERIAL", primary_key=True)
    nome = Field("VARCHAR")
    idade = Field("INTEGER")
    #universidade = Field("INTEGER", foreign_key="universidade(id)")
    # universidade = OneToMany(Universidade, on_delete="CASCADE")

class Endereco(Model):
    _table_name ="endereco"
    id = Field("SERIAL",primary_key=True)
    logradouro = Field("VARCHAR")
    estado = Field("VARCHAR")
    cidade = Field("VARCHAR")
    aluno = OneToOne(Aluno,on_delete="CASCADE")

db_connection.create_table(Aluno)
db_connection.create_table(Endereco)

a = Aluno(nome= "Lucas",idade= 25)
db_connection.save(a)
print("Aluno salvo")
e = Endereco(logradouro = "joao viera carneiro 980 Pedro Gondim",estado="PB",cidade="Joao Pessoa",aluno= 1)
db_connection.save(e)
print("Endereco salvo")




