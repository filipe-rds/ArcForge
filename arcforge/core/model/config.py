import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
print(os.path.exists('config.env'))
print(load_dotenv())

# Variáveis de ambiente para parâmetros de conexão
DB_NAME = os.getenv("DB_NAME",)
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Valor padrão de porta 5432

print("DB_NAME:", DB_NAME)
print("DB_USER:", DB_USER)
print("DB_PASSWORD:", DB_PASSWORD)
print("DB_HOST:", DB_HOST)
print("DB_PORT:", DB_PORT)

# Validar se todas as variáveis de ambiente estão definidas
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    raise Exception("Parâmetros de conexão não estão definidos no arquivo .env")
