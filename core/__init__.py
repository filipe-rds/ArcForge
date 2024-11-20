from .database.connection import init_db
from .utils.exceptions import FrameworkError

# Inicialização da variável global db
db = None  # Declarando db como uma variável global, mas sem conexão ainda.


def setup_database():
    global db
    if db is not None:
        raise FrameworkError("Banco de dados já inicializado.")  # Evita inicialização repetida

    try:
        db = init_db()  # Inicializa a conexão com o banco
        db.create_tables()  # Cria as tabelas, se necessário
        print("Banco de dados configurado com sucesso.")
    except Exception as e:
        raise FrameworkError(f"Erro ao configurar o banco de dados: {e}")


def teardown_database():
    """Função para fechar a conexão com o banco de dados."""
    global db
    if db is not None:
        db.close()  # Fechar a conexão com o banco de dados
        print("Conexão com o banco de dados fechada.")
    else:
        print("Nenhuma conexão ativa com o banco de dados para fechar.")


if __name__ == "__main__":
    try:
        setup_database()
        # Aqui você pode colocar a lógica principal da aplicação ou do framework

    except FrameworkError as e:
        print(f"Erro durante a configuração: {e}")
    finally:
        teardown_database()  # Certifica-se de fechar a conexão ao final
