from arcforge.core.model.model import *
from arcforge.core.db.db_connection import *

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
    universidade = ManyToOne(Universidade, on_delete="CASCADE")

db_connection.create_table(Universidade)
db_connection.create_table(Aluno)


u = Universidade(nome="UFPB",endereco="Joao Pessoa")
db_connection.save(u)
u = Universidade(nome="UFPB",endereco="Joao Pessoa")
db_connection.save(u)
#print("Universidade salva")
#print(u.id)
a = Aluno(nome= "Lucas",idade= 25,universidade=u.id)
#print("ID do aluno sem ser inserido no banco: ")
#print(a.id)
db_connection.save(a)

a = Aluno(nome= "Lucas",idade= 25,universidade=u.id)
db_connection.save(a)
#print("Aluno salvo")
#print(a.id)
#db_connection.save(a)
# u2 = Universidade(nome="UFPE",endereco="Rio de Janeiro")
# db_connection.save(u2)
# print("Universidade salva")
# print(u2.id)
# a2 = Aluno(nome= "Lucas",idade= 25,universidade=u2.id)


# arrayDeParametros = [parametro1,parametro2,parametro3,parametro4,parametro5]


# parametros = {
#     'parametro1': 'nome',
#     'parametro2': 'idade',
#     'parametro3': 'aluno',
#     'parametro4': 'id',
#     'parametro5': 10
# }

# query = f"select {parametros['parametro1']},{parametros['parametro2']} from parametro3 where parametro4 = parametro5;"

# query = f"select x1,x2 from x3 where x4 = x4;"

# realizarConsulta(query,parametros)

id = 1

#consulta = "select u.nome,u.endereco from Universidade u join Aluno a on u.id = a.universidade where a.nome = %s ;"
consulta = "select nome,id from Aluno where nome = %s ;"


params = ["Lucas"]


print(db_connection.transformarArrayEmObjetos(Aluno,db_connection.query(consulta,params)))

# u = db_connection.transformarArrayEmObjeto(Universidade,db_connection.buscarPeloId(Universidade,1))
# print(u.id)
# print(u.nome)
# print(u.endereco)
# print(isinstance(u, Universidade)) 
# print(u)
# print(vars(u))


