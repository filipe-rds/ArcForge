import psycopg
from contextlib import contextmanager
from arcforge.core.db.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
import logging

# -----------------------------------------------------------------------------
# Configuração de Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------

class DatabaseConnection:
    """Classe estática para gerenciar a conexão com o banco de dados."""

    # Atributo estático para armazenar a conexão
    _connection = None

    @staticmethod
    def set_connection():
        """Estabelece uma conexão com o banco de dados, se ainda não estiver conectada."""
        if DatabaseConnection._connection is None:
            try:
                DatabaseConnection._connection = psycopg.connect(
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

    @staticmethod
    def start_connection():
        """Inicializa a conexão com o banco de dados."""
        DatabaseConnection.set_connection()

    @staticmethod
    def close_connection():
        """Fecha a conexão com o banco de dados, se ela estiver ativa."""
        if DatabaseConnection._connection:
            DatabaseConnection._connection.close()
            DatabaseConnection._connection = None
            logger.info("Conexão fechada com sucesso.")
        else:
            logger.info("Nenhuma conexão ativa para ser fechada.")

    @staticmethod
    def get_connection():
        """Retorna a conexão ativa ou inicializa uma nova conexão, se necessário."""
        DatabaseConnection.set_connection()
        return DatabaseConnection._connection

    @staticmethod
    @contextmanager
    def get_cursor():
        """Fornece um cursor gerenciado para operações no banco de dados."""
        if DatabaseConnection._connection is None:
            DatabaseConnection.set_connection()
        cursor = DatabaseConnection._connection.cursor()
        try:
            yield cursor
        except psycopg.Error as e:
            DatabaseConnection._connection.rollback()
            logger.error("Erro durante operação com o cursor. Rollback executado.")
            raise e
        finally:
            cursor.close()

__all__ = ["DatabaseConnection","logging"]