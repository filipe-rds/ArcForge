import threading
import psycopg
from psycopg import sql
from typing import Type, Any, List, Dict

from arcforge.core.db.manager import DatabaseManager
from arcforge.core.db.util import Util
import logging

# -----------------------------------------------------------------------------
# Configuração de Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------

class Singleton(type):
    _instances = {}
    _lock = threading.Lock()  # Lock para evitar problemas em ambientes multithread

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DAO(metaclass=Singleton):
    def __init__(self):
        self.__db_manager = DatabaseManager()

    def __get_connection(self):
        """Obtém a conexão ativa ou a reconecta, se necessário."""
        connection = self.__db_manager.get_connection()
        return connection

    def create_table(self, base_model):
        """Cria a tabela no banco de dados com base no modelo fornecido."""
        fields_sql = base_model._generate_fields()
        create_table_query = sql.SQL(""" 
            CREATE TABLE IF NOT EXISTS {table} (
                {fields}
            );
        """).format(
            table=sql.Identifier(base_model._table_name),
            fields=sql.SQL(fields_sql)
        )
        try:
            with self.__get_connection().cursor() as cursor:  # Usando a conexão obtida dinamicamente
                cursor.execute(create_table_query)
                self.__get_connection().commit()  # Commit na conexão
                logger.info(f"Tabela {base_model._table_name} criada com sucesso.")
        except psycopg.Error as e:
            logger.error(f"Erro ao criar a tabela {base_model._table_name}: {e}")
            raise

    def delete_table(self, base_model):
        """Deleta a tabela do banco de dados com base no modelo fornecido, removendo também as dependências (cascade)."""
        drop_table_query = sql.SQL("DROP TABLE IF EXISTS {table} CASCADE;").format(
            table=sql.Identifier(base_model._table_name)
        )
        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(drop_table_query)
                self.__get_connection().commit()
                logger.info(f"Tabela {base_model._table_name} deletada com sucesso (cascade).")
        except psycopg.Error as e:
            logger.error(f"Erro ao deletar a tabela {base_model._table_name}: {e}")
            raise

    def save(self, model_instance):
        """Salva (INSERT) a instância no banco de dados."""
        Util.validationType(model_instance.__class__, model_instance)
        columns = [attr for attr in model_instance.__dict__ if not attr.startswith("_")]
        values = [getattr(model_instance, col) for col in columns]
        placeholders = [sql.Placeholder() for _ in columns]

        query = sql.SQL(""" 
            INSERT INTO {table} ({fields})
            VALUES ({placeholders})
            RETURNING id;
        """).format(
            table=sql.Identifier(model_instance._table_name),
            fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(", ").join(placeholders)
        )
        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(query, values)
                self.__get_connection().commit()
                model_instance.id = cursor.fetchone()[0]
                logger.info(f"Instância de {model_instance.__class__.__name__} salva com sucesso.")
                return model_instance
        except psycopg.Error as e:
            logger.error(f"Erro ao salvar a instância {model_instance._table_name}: {e}")
            raise

    def update(self, model_instance):
        """Atualiza (UPDATE) a instância no banco de dados."""
        Util.validationType(model_instance.__class__, model_instance)
        model_id = getattr(model_instance, "id", None)
        if not model_id:
            raise ValueError("Não é possível realizar o UPDATE sem um ID válido.")

        columns = [attr for attr in model_instance.__dict__ if not attr.startswith("_") and attr != "id"]
        set_clauses = [sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder()) for col in columns]
        values = [getattr(model_instance, col) for col in columns]

        query = sql.SQL(""" 
            UPDATE {table}
            SET {set_clause}
            WHERE id = {id_placeholder}
        """).format(
            table=sql.Identifier(model_instance._table_name),
            set_clause=sql.SQL(", ").join(set_clauses),
            id_placeholder=sql.Placeholder()
        )
        values.append(model_id)
        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(query, values)
                self.__get_connection().commit()
                logger.info(f"Instância de {model_instance.__class__.__name__} atualizada com sucesso.")
                return model_instance
        except psycopg.Error as e:
            logger.error(f"Erro ao atualizar a instância {model_instance._table_name}: {e}")
            raise

    def delete(self, model_instance_or_id):
        """Deleta um registro do banco passando um objeto da classe modelo ou um ID."""
        model_class = model_instance_or_id.__class__ if not isinstance(model_instance_or_id, int) else None
        object_id = model_instance_or_id.id if model_class else model_instance_or_id

        if not object_id:
            raise ValueError("É necessário um ID válido para deletar o registro.")

        query = sql.SQL(""" 
            DELETE FROM {table} WHERE id = %s;
        """).format(
            table=sql.Identifier(model_class._table_name if model_class else "table_desconhecida")
        )
        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(query, (object_id,))
                self.__get_connection().commit()
                logger.info(f"Registro com ID {object_id} deletado com sucesso.")
        except psycopg.Error as e:
            logger.error(f"Erro ao deletar registro com ID {object_id}: {e}")
            raise

    def read(self, model_class, object_id):
        """Busca um objeto pelo ID no banco de dados."""
        query = sql.SQL(""" 
            SELECT * FROM {table} WHERE id = %s;
        """).format(
            table=sql.Identifier(model_class._table_name)
        )
        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(query, (object_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return Util._row_to_object(model_class, row, columns)
                return None
        except psycopg.Error as e:
            logger.error(f"Erro ao buscar {model_class.__name__} com ID {object_id}: {e}")
            raise

    def find_all(self, model_class) -> List[Any]:
        """Executa uma consulta SQL personalizada."""
        query = sql.SQL(""" 
            SELECT * FROM {table};
        """).format(
            table=sql.Identifier(model_class._table_name)
        )
        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                objects = [Util._row_to_object(model_class, row, columns) for row in rows]

                if len(objects) == 1:
                    return objects[0]  # Retorna o objeto diretamente
                return objects  # Retorna a lista de objetos
        except psycopg.Error as e:
            logger.error(f"Erro ao executar a consulta: {e}")
            raise