import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from ..models.fields import *
from ..utils.exceptions import *

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Variáveis de ambiente para parâmetros de conexão
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")

# Validar se todas as variáveis de ambiente estão definidas
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST]):
    raise FrameworkError("Parâmetros de conexão não estão definidos no arquivo .env")


class DatabaseConnection:
    _instance = None  # Instância única da conexão

    def __new__(cls, *args, **kwargs):
        """Garante que a conexão seja instanciada uma única vez."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT):
        if not hasattr(self, 'connection'):  # Evita reconfiguração se a conexão já foi estabelecida
            self.dbname = dbname
            self.user = user
            self.password = password
            self.host = host
            self.port = port
            self.connection = None
            self.cursor = None
            self.models = []  # Lista para armazenar modelos mapeados
            self.connect()

    def connect(self):
        """Estabelece a conexão com o banco de dados PostgreSQL."""
        if not self.connection:
            try:
                # Conectar ao banco de dados usando parâmetros do .env
                self.connection = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port
                )
                self.cursor = self.connection.cursor()
                print("Conexão bem-sucedida ao PostgreSQL.")
            except Exception as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
                raise

    def close(self):
        """Fecha a conexão e o cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        """Executa uma query SQL."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f"Erro ao executar a query: {e}")
            self.connection.rollback()

    def fetch_all(self, query, params=None):
        """Executa uma query e retorna todos os resultados."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return None

    def register_model(self, model_class):
        """Registra um modelo no sistema."""
        self.models.append(model_class)

    def create_tables(self):
        """Cria as tabelas no banco de dados com base nos modelos registrados, se elas não existirem."""
        for model in self.models:
            table_name = model.__name__.lower()  # Nome da tabela baseado na classe
            # Verificar se a tabela já existe
            if not self._table_exists(table_name):
                create_table_query = self._generate_create_table_query(model)
                self.execute_query(create_table_query)
            else:
                print(f"Tabela {table_name} já existe, não será criada.")

    def _table_exists(self, table_name):
        """Verifica se a tabela já existe no banco de dados."""
        check_table_query = sql.SQL("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """)
        self.cursor.execute(check_table_query, (table_name,))
        return self.cursor.fetchone()[0]  # Retorna True se a tabela existir, False caso contrário

    def _generate_create_table_query(self, model):
        """Gera a query para criar a tabela a partir de um modelo."""
        table_name = model.__name__.lower()  # Nome da tabela baseado na classe
        columns = []

        # Itera sobre os campos definidos no modelo
        for field_name, field in model.__annotations__.items():
            column_def = f"{field_name} {field.field_type}"
            # Se o campo for uma chave estrangeira, adicionar a referência
            if isinstance(field, ForeignKey):
                column_def = f"{field_name} INTEGER REFERENCES {field.ref_table}({field.ref_column})"
            columns.append(column_def)

        columns_str = ", ".join(columns)
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});"
        return create_table_query

    def get_session(self):
        """Retorna a conexão atual para interação com o banco"""
        return self.connection


# Função global para inicializar o banco de dados
def init_db():
    """Inicializa a conexão com o banco de dados e retorna a instância da conexão."""
    return DatabaseConnection()
