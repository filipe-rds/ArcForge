from arcforge.core.model.model import *
from arcforge.core.db.connection import *
from datetime import datetime
from colorama import Fore, Style, init

# Inicializando o colorama
init(autoreset=True)

db_connection = DatabaseConnection()

# Modelando os campos com tipos diversos
class Aluno(Model):
    _table_name = "aluno"
    id = Field("SERIAL", primary_key=True)
    nome = Field("VARCHAR")
    idade = Field("INTEGER")
    nota = Field("REAL")
    data_nascimento = Field("DATE")
    ativo = Field("BOOLEAN")

# Criação da tabela Aluno
print(f"\n{Style.BRIGHT}{Fore.BLUE}=== CRIAÇÃO DE TABELA ===")
db_connection.create_table(Aluno)
print(f"{Fore.GREEN}Tabela 'Aluno' criada com sucesso")

# Inserção de dados
print(f"\n{Style.BRIGHT}{Fore.BLUE}=== INSERÇÃO DE DADOS ===")

# Dados válidos
print(f"\n{Fore.YELLOW}Inserindo Aluno: {Style.BRIGHT}Carlos Silva (Idade: 20, Nota: 8.5, Nascimento: 2003-05-10, Ativo: True)")
aluno_carlos = Aluno(nome="Carlos Silva", idade=20, nota=8.5, data_nascimento='2003-05-10', ativo=True)

# Tentando salvar os dados
try:
    db_connection.save(aluno_carlos)
    print(f"{Fore.GREEN}Registro inserido com sucesso: {Style.BRIGHT}{aluno_carlos}")
except Exception as e:
    print(f"{Fore.RED}Erro ao inserir dados: {e}")

# Dados inválidos
print(f"\n{Fore.YELLOW}Inserindo Aluno com dados inválidos (Idade: 17, Nota: 11.0, Data de Nascimento: formato inválido, Ativo: True)")

aluno_invalido = Aluno(nome="João Costa", idade=17, nota=11.0, data_nascimento='05/10/2003', ativo=True)

# Tentando salvar os dados inválidos
try:
    db_connection.save(aluno_invalido)
    print(f"{Fore.GREEN}Registro inserido com sucesso: {Style.BRIGHT}{aluno_invalido}")
except Exception as e:
    print(f"{Fore.RED}Erro ao inserir dados: {e}")

# Consultando os dados
print(f"\n{Style.BRIGHT}{Fore.BLUE}=== CONSULTA DE DADOS ===")
print(f"\n{Fore.YELLOW}Consultando todos os alunos")
result = db_connection.query(Aluno)

if result:
    print(f"\n{Fore.GREEN}Resultado encontrado para os alunos cadastrados:\n")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}ID | Nome               | Idade | Nota  | Data Nascimento | Ativo")
    print(f"{Style.BRIGHT}{Fore.MAGENTA}---+--------------------+-------+-------+------------------+-------")

    for aluno in result:
        print(f"{aluno.id:<3} | {aluno.nome:<18} | {aluno.idade:<5} | {aluno.nota:<5} | {aluno.data_nascimento} | {aluno.ativo}")
else:
    print(f"{Fore.RED}Nenhum aluno encontrado.")
