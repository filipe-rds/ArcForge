import psycopg
import threading
from contextlib import contextmanager
from arcforge.core.db.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
import logging


# -----------------------------------------------------------------------------
# Configuração de Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Design Pattern: Singleton
# Garante que apenas uma instância de DatabaseManager seja criada.
# -----------------------------------------------------------------------------
class Singleton(type):
    _instances = {}
    _lock = threading.Lock()  # Lock para evitar problemas em ambientes multithread

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseManager(metaclass=Singleton):
    def __init__(self):
        self._connection = None
        self.connect()  # Estabelece a conexão logo na criação do objeto

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self._connection = psycopg.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
            )
            logger.info("Conexão estabelecida com sucesso.")
        except psycopg.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def get_connection(self):
        """
        Retorna a conexão ativa.
        Verifica se a conexão foi perdida e reconecta, se necessário.
        """
        # Aqui assumimos que o atributo 'closed' indica o status da conexão:
        # Em psycopg2, 'closed' é 0 se a conexão estiver aberta.
        if self._connection is None or self._connection.closed:
            logger.info("Conexão perdida ou inativa. Reconectando...")
            self.connect()
        return self._connection

    def close_connection(self):
        """Fecha a conexão com o banco de dados, se ela estiver ativa."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
            logger.info("Conexão fechada com sucesso.")
        else:
            logger.info("Nenhuma conexão ativa para ser fechada.")

    @contextmanager
    def get_cursor(self):
        """
        Fornece um cursor gerenciado para operações no banco de dados.
        Verifica a conexão e realiza rollback em caso de erro.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        except psycopg.Error as e:
            conn.rollback()
            logger.error("Erro durante operação com o cursor. Rollback executado.")
            raise e
        finally:
            cursor.close()