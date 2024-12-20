import psycopg
from colorama import Fore, Style, init

# Inicializando o colorama
init(autoreset=True)

try:
    # Tentativa de conexão com o banco de dados PostgreSQL
    connection = psycopg.connect(
        host="localhost",
        dbname="test",
        user="postgres",
        password="ifpb",
        port=5432
    )
    print(f"{Fore.GREEN}{Style.BRIGHT}Conexão bem-sucedida com o PostgreSQL!")

    # Fechando a conexão após o uso
    connection.close()

except Exception as e:
    print(f"{Fore.RED}{Style.BRIGHT}Erro ao conectar ao PostgreSQL: {e}")

