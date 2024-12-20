from arcforge.core.model.model import *
from arcforge.core.db.connection import *
from colorama import Fore, Style, init

# Inicializando o colorama
init(autoreset=True)

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
    universidade = OneToOne(Universidade, on_delete="CASCADE")  # Relacionamento OneToOne


class Aluno(Model):
    _table_name = "aluno"
    id = Field("SERIAL", primary_key=True)
    nome = Field("VARCHAR")
    idade = Field("INTEGER")
    universidade = ManyToOne(Universidade, on_delete="CASCADE")
    curso = ManyToOne(Curso, on_delete="CASCADE")


# Criação de tabelas
print(f"\n{Style.BRIGHT}{Fore.BLUE}=== CRIAÇÃO DE TABELAS ===")
db_connection.create_table(Universidade)
print(f"{Fore.GREEN}Tabela 'Universidade' criada com sucesso")
db_connection.create_table(Curso)
print(f"{Fore.GREEN}Tabela 'Curso' criada com sucesso")
db_connection.create_table(Aluno)
print(f"{Fore.GREEN}Tabela 'Aluno' criada com sucesso")

# Inserção de dados
print(f"\n{Style.BRIGHT}{Fore.BLUE}=== INSERÇÃO DE DADOS ===")

# Inserindo universidades
print(f"\n{Fore.YELLOW}Inserindo Universidade: {Style.BRIGHT}IFPB")
ifpb = Universidade(nome="IFPB", endereco="João Pessoa")
db_connection.save(ifpb)
print(f"{Fore.GREEN}Registro inserido: {Style.BRIGHT}{ifpb}")

print(f"\n{Fore.YELLOW}Inserindo Universidade: {Style.BRIGHT}UFPB")
ufpb = Universidade(nome="UFPB", endereco="João Pessoa")
db_connection.save(ufpb)
print(f"{Fore.GREEN}Registro inserido: {Style.BRIGHT}{ufpb}")

# Inserindo cursos
print(f"\n{Fore.YELLOW}Inserindo Curso: {Style.BRIGHT}TSI (Universidade: IFPB)")
curso_tsi = Curso(nome="TSI", universidade=ifpb.id)
db_connection.save(curso_tsi)
print(f"{Fore.GREEN}Registro inserido: {Style.BRIGHT}{curso_tsi}")

print(f"\n{Fore.YELLOW}Inserindo Curso: {Style.BRIGHT}Engenharia de Software (Universidade: UFPB)")
curso_es = Curso(nome="Engenharia de Software", universidade=ufpb.id)
db_connection.save(curso_es)
print(f"{Fore.GREEN}Registro inserido: {Style.BRIGHT}{curso_es}")

# Inserindo alunos
print(f"\n{Fore.YELLOW}Inserindo Aluno: {Style.BRIGHT}Filipe Rodrigues (Universidade: IFPB, Curso: TSI)")
aluno_filipe = Aluno(nome="Filipe Rodrigues", idade=25, universidade=ifpb.id, curso=curso_tsi.id)
db_connection.save(aluno_filipe)
print(f"{Fore.GREEN}Registro inserido: {Style.BRIGHT}{aluno_filipe}")

print(f"\n{Fore.YELLOW}Inserindo Aluno: {Style.BRIGHT}Gabriel Félix (Universidade: IFPB, Curso: TSI)")
aluno_gabriel = Aluno(nome="Gabriel Félix", idade=22, universidade=ifpb.id, curso=curso_tsi.id)
db_connection.save(aluno_gabriel)
print(f"{Fore.GREEN}Registro inserido: {Style.BRIGHT}{aluno_gabriel}")

print(f"\n{Fore.YELLOW}Inserindo Aluno: {Style.BRIGHT}Lucas Pedro (Universidade: IFPB, Curso: TSI)")
aluno_lucas = Aluno(nome="Lucas Pedro", idade=23, universidade=ifpb.id, curso=curso_tsi.id)
db_connection.save(aluno_lucas)
print(f"{Fore.GREEN}Registro inserido: {Style.BRIGHT}{aluno_lucas}")

# Atualização de um aluno (opcional)
print(f"\n{Style.BRIGHT}{Fore.BLUE}=== ATUALIZAÇÃO DE REGISTRO ===")
aluno_filipe.idade = 22
db_connection.update(aluno_filipe)
print(f"{Fore.GREEN}Aluno atualizado: {Style.BRIGHT}{aluno_filipe}")

# Consultando os dados
print(f"\n{Style.BRIGHT}{Fore.BLUE}=== CONSULTA DE DADOS ===")
print(f"\n{Fore.YELLOW} {Style.BRIGHT}Consultando alunos da universidade IFPB que estão no curso de TSI")
result = db_connection.query(
    Aluno,
    universidade_nome="IFPB",
    curso_nome="TSI",
)

# Exibindo os resultados
if result:
    print(f"\n{Fore.GREEN}Resultado encontrado para os critérios fornecidos:\n")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}ID | Nome              | Idade | Universidade        | Curso")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}---+-------------------+-------+---------------------+-------------------------")

    for aluno in result:
        # Exibindo as informações do aluno
        print(f"{aluno.id:<3} | {aluno.nome:<18} | {aluno.idade:<5} | {aluno.universidade:<20} | {aluno.curso}")
else:
    print(f"{Fore.RED}Nenhum resultado encontrado para os critérios fornecidos.")
