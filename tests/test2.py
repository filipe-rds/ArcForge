import unittest
import psycopg
from colorama import Fore, Style, init

# Inicializando o colorama para visualização de mensagens coloridas (opcional)
init(autoreset=True)

class TestDBConnection(unittest.TestCase):
    def test_connection(self):
        """
        Testa se é possível estabelecer uma conexão com o banco de dados PostgreSQL.

        Padrão Aplicado:
        - Facade: A API do psycopg encapsula a complexidade de estabelecer a conexão.
        - TDD: O teste verifica se a conexão é estabelecida com sucesso; caso contrário, falha.
        """
        try:
            connection = psycopg.connect(
                host="localhost",
                dbname="test",
                user="postgres",
                password="ifpb",
                port=5432
            )
            # Verifica se a conexão foi criada com sucesso.
            self.assertIsNotNone(connection, "A conexão não deve ser None")
            print(f"{Fore.GREEN}{Style.BRIGHT}Conexão bem-sucedida com o PostgreSQL!")
            connection.close()
        except Exception as e:
            self.fail(f"{Fore.RED}{Style.BRIGHT}Erro ao conectar ao PostgreSQL: {e}")

if __name__ == "__main__":
    unittest.main()
