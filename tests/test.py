from arcforge.core.model.model import *
from arcforge.core.db.connection import *

db_connection = DatabaseConnection()


class Universidade(Model):
    _table_name = "universidade"
    id = Field("SERIAL", primary_key=True)
    nome = Field("VARCHAR")
    endereco = Field("VARCHAR")


class Curso(Model):
    _table_name = "curso"
    id = Field("SERIAL", primary_key=True)
    nome = Field("VARCHAR")
    universidade = ManyToOne(Universidade, on_delete="CASCADE")


class Aluno(Model):
    _table_name = "aluno"
    id = Field("SERIAL", primary_key=True)
    nome = Field("VARCHAR")
    idade = Field("INTEGER")
    universidade = ManyToOne(Universidade, on_delete="CASCADE")
    curso = ManyToOne(Curso, on_delete="CASCADE")


# Criação de tabelas
print("\n### Criando tabelas ###")
db_connection.create_table(Universidade)
print("Tabela Universidade criada")
db_connection.create_table(Curso)
print("Tabela Curso criada")
db_connection.create_table(Aluno)
print("Tabela Aluno criada")

# Inserção de dados
print("\n### Inserindo dados ###")
# Inserindo universidades
print("Inserindo Universidade: UFPB")
ufpb = Universidade(nome="UFPB", endereco="Joao Pessoa")
db_connection.save(ufpb)
print(f"Registro inserido: {ufpb}")

print("Inserindo Universidade: UFPE")
ufpe = Universidade(nome="UFPE", endereco="Recife")
db_connection.save(ufpe)
print(f"Registro inserido: {ufpe}")

print("Inserindo Universidade: UFPE (local: Rio de Janeiro)")
ufpe_rj = Universidade(nome="UFPE", endereco="Rio de Janeiro")
db_connection.save(ufpe_rj)
print(f"Registro inserido: {ufpe_rj}")

# Inserindo curso
print("Inserindo Curso: Engenharia de Software (universidade: UFPE)")
curso_es = Curso(nome="Engenharia de Software", universidade=ufpe.id)
db_connection.save(curso_es)
print(f"Registro inserido: {curso_es}")

# Inserindo alunos
print("Inserindo Aluno: Lucas (universidade: UFPE, curso: Engenharia de Software)")
aluno_lucas = Aluno(nome="Lucas", idade=25, universidade=ufpe.id, curso=curso_es.id)
db_connection.save(aluno_lucas)
print(f"Registro inserido: {aluno_lucas}")

print("Inserindo Aluno: Lucas (universidade: UFPE (RJ), curso: Engenharia de Software)")
aluno_filipe = Aluno(nome="Lucas", idade=25, universidade=ufpe_rj.id, curso=curso_es.id)
db_connection.save(aluno_filipe)
print(f"Registro inserido: {aluno_filipe}")

# Atualizando registro de aluno
print("\n### Atualizando registro ###")
aluno_filipe.nome = "Filipe Rodrigues"
db_connection.update(aluno_filipe)
print(f"Aluno atualizado: {aluno_filipe}")

# Consultando os dados
print("\n### Consultando dados ###")
result = db_connection.query(
    Aluno,
    universidade_endereco="Rio de Janeiro",
    curso_nome="Engenharia de Software",
    aluno_nome="Filipe Rodrigues"
)
print(f"Resultado da consulta: {result}")

# Validando resultado
if result:
    print("\n### Dados retornados da consulta ###")
    for row in result:
        print(row)
else:
    print("Nenhum resultado encontrado para os critérios fornecidos.")
