import threading
from typing import List, Any

import psycopg
from psycopg import sql

from arcforge.core.db.dao import *
import logging

from arcforge.core.db.manager import DatabaseManager
from arcforge.core.db.util import Util

# -----------------------------------------------------------------------------
# Configuração de Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Singleton(type):
    _instances = {}
    _lock = threading.Lock()  # Lock para evitar problemas em ambientes multithread

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Query(metaclass=Singleton):

    def __init__(self):
        self.db_manager = DatabaseManager()

    def __get_connection(self):
        """Obtém a conexão ativa ou a reconecta, se necessário."""
        connection = self.db_manager.get_connection()
        return connection

    def execute_sql(self, query: str, params: List[Any]) -> List[Any]:
        """Executa uma consulta SQL personalizada."""
        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except psycopg.Error as e:
            logger.error(f"Erro ao executar a consulta: {e}")
            raise

    def execute(self, base_model, **filters) -> List[Any]:
        """
        Executa uma consulta no banco de dados com base nos filtros fornecidos, inferindo automaticamente
        os joins necessários a partir das relações definidas no modelo. Suporta ORDER BY e GROUP BY.

        Parâmetros:
            base_model: Classe do modelo base para a consulta
            filters: Filtros podendo incluir condições WHERE, ORDER BY e GROUP BY

        Retorno:
            List[Any]: Lista de objetos do domínio
        """
        try:
            # Construção da query base
            base_table = sql.Identifier(base_model._table_name)
            base_query = sql.SQL("SELECT {base_table}.* FROM {base_table}").format(
                base_table=base_table
            )

            # Geração automática de JOINS
            join_clauses = []
            relationships = getattr(base_model, "_relationships", [])
            joined_tables = {base_model._table_name: True}  # Tabelas já incluídas

            for rel in relationships:
                ref_table = rel["ref_table"]
                base_column = rel["field_name"]
                ref_field = rel.get("ref_field", "id")

                if ref_table not in joined_tables:
                    join_clause = sql.SQL(" JOIN {ref_table} ON {base_table}.{base_column} = {ref_table}.{ref_field}").format(
                        ref_table=sql.Identifier(ref_table),
                        base_table=base_table,
                        base_column=sql.Identifier(base_column),
                        ref_field=sql.Identifier(ref_field)
                    )
                    join_clauses.append(join_clause)
                    joined_tables[ref_table] = True

            # Processamento dos filtros
            order_by = filters.pop('order_by', None)
            group_by = filters.pop('group_by', None)

            filter_clauses = []
            filter_values = []
            for column, value in filters.items():
                # Nova lógica corrigida para identificação de tabela/coluna
                if "." in column:
                    table, column_name = column.split(".", 1)
                else:
                    table = base_model._table_name
                    column_name = column

                filter_clauses.append(
                    sql.SQL("{table}.{column} = %s").format(
                        table=sql.Identifier(table),
                        column=sql.Identifier(column_name)
                    )
                )
                filter_values.append(value)

            # Construção das cláusulas
            where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(filter_clauses) if filter_clauses else sql.SQL("")

            # GROUP BY
            group_by_sql = sql.SQL("")
            if group_by:
                group_columns = [group_by] if isinstance(group_by, str) else group_by
                group_clauses = []
                for col in group_columns:
                    if "." in col:
                        table, column = col.split(".", 1)
                        group_clauses.append(sql.SQL("{table}.{column}").format(
                            table=sql.Identifier(table),
                            column=sql.Identifier(column)
                        ))
                    else:
                        group_clauses.append(sql.SQL("{table}.{column}").format(
                            table=base_table,
                            column=sql.Identifier(col)
                        ))
                group_by_sql = sql.SQL(" GROUP BY ") + sql.SQL(", ").join(group_clauses)

            # ORDER BY
            order_by_sql = sql.SQL("")
            if order_by:
                order_columns = [order_by] if isinstance(order_by, str) else order_by
                order_clauses = []
                for col in order_columns:
                    parts = col.strip().split()
                    column_part = parts[0]
                    direction = parts[1].upper() if len(parts) > 1 and parts[1].upper() in ('ASC', 'DESC') else ''

                    if "." in column_part:
                        table, column = column_part.split(".", 1)
                        clause = sql.SQL("{table}.{column}").format(
                            table=sql.Identifier(table),
                            column=sql.Identifier(column)
                        )
                    else:
                        clause = sql.SQL("{table}.{column}").format(
                            table=base_table,
                            column=sql.Identifier(column_part)
                        )

                    if direction:
                        clause += sql.SQL(f" {direction}")

                    order_clauses.append(clause)

                order_by_sql = sql.SQL(" ORDER BY ") + sql.SQL(", ").join(order_clauses)

            # Query final
            full_query = (
                    base_query +
                    sql.SQL(" ").join(join_clauses) +
                    where_clause +
                    group_by_sql +
                    order_by_sql
            )

            # Execução
            with self.__get_connection().cursor() as cursor:
                cursor.execute(full_query, filter_values)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # Converte as linhas em objetos
                objects = [Util._row_to_object(base_model, row, columns) for row in rows]

                # Retorna o objeto diretamente se houver apenas um resultado
                if len(objects) == 1:
                    return objects[0]  # Retorna o objeto diretamente
                return objects  # Retorna a lista de objetos

        except psycopg.Error as e:
            logger.error(f"Erro ao executar a consulta: {e}")
            raise