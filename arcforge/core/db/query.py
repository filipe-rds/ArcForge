from arcforge.core.db.util import Util
from typing import List, Any
import psycopg
from psycopg import sql
import logging

# -----------------------------------------------------------------------------
# Configuração de Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Query:

    def __init__(self):
        from .manager import DatabaseManager

        self.__db_manager = DatabaseManager()

    def __get_connection(self):
        """Obtém a conexão ativa ou a reconecta, se necessário."""
        connection = self.__db_manager.get_connection()
        return connection

    def table_exists(self, table_name):
        """Verifica se uma tabela já existe no banco de dados."""
        query = sql.SQL("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = %s
            );
        """)

        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(query, (table_name,))
                return cursor.fetchone()[0]  # Retorna True se a tabela existir, False caso contrário
        except psycopg.Error as e:
            logger.error(f"Erro ao verificar a existência da tabela {table_name}: {e}")
            raise

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

    def delete(self, model_class, object_id):
        """Deleta um registro do banco passando um objeto da classe modelo ou um ID."""

        if not isinstance(object_id, int):
            raise TypeError(f"O ID deve ser um número inteiro. Recebido: {type(object_id)}")


        query = sql.SQL(""" 
            DELETE FROM {table} WHERE id = %s;
        """).format(
            table=sql.Identifier(model_class._table_name)
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
                cursor.execute(query, [object_id])
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
            SELECT * FROM {table} ORDER BY id;
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

    def execute_sql(self, query: str, params: List[Any]) -> List[Any]:
        try:
            with self.__get_connection().cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except psycopg.Error as e:
            logger.error(f"Erro ao executar a consulta: {e}")
            raise

    def execute(self, base_model, **kwargs) -> Any:
        try:
            # Extrai parâmetros especiais
            where_filters = kwargs.pop('where', {})
            having_filters = kwargs.pop('having', {})
            order_by = kwargs.pop('order_by', None)
            group_by = kwargs.pop('group_by', None)
            select_fields = kwargs.pop('select', None)
            single_result = kwargs.pop('single_result', False)  # Novo parâmetro para indicar retorno de resultado único

            # 1. Construção do SELECT
            base_table = sql.Identifier(base_model._table_name)

            if select_fields:
                select_items = []
                for field in select_fields:
                    # Caso de expressão com alias (ex: COUNT(*) AS total)
                    if ' AS ' in field.upper():
                        # Usa SQL diretamente, pois já está formatado corretamente
                        select_items.append(sql.SQL(field))
                    elif '(' in field:
                        # Expressão sem alias explícito
                        select_items.append(sql.SQL(field))
                    else:
                        # Campo simples
                        select_items.append(sql.Identifier(field))
                select_clause = sql.SQL(', ').join(select_items)
            else:
                select_clause = sql.SQL('*')

            # 2. Geração automática de JOINS
            join_clauses = Util._generate_joins(base_model, base_table)

            # 3. Processamento WHERE
            where_clauses = []
            filter_values = []
            for key, value in where_filters.items():
                if "__" in key:
                    field, operator = key.split("__", 1)
                    operator = operator.lower()
                else:
                    field, operator = key, "eq"

                # Mapeia operadores
                sql_operator = {
                    "eq": "=", "like": "LIKE", "ilike": "ILIKE",
                    "gt": ">", "lt": "<", "gte": ">=", "lte": "<="
                }.get(operator, "=")

                # Adiciona wildcards para operadores de texto
                if operator in ("like", "ilike") and "%" not in str(value):
                    value = f"%{value}%"

                # Resolve referência da coluna
                table, column = Util._parse_column_reference(base_model, field)
                if table:  # Se não for expressão SQL
                    col_ref = sql.SQL("{table}.{col}").format(
                        table=sql.Identifier(table),
                        col=sql.Identifier(column)
                    )
                else:
                    col_ref = sql.SQL(column)

                # Constrói cláusula WHERE
                where_clauses.append(sql.SQL("{col} {op} %s").format(col=col_ref, op=sql.SQL(sql_operator)))
                filter_values.append(value)

            where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_clauses) if where_clauses else sql.SQL("")

            # 4. Processamento HAVING - Usando o novo método
            having_clause, having_values = Util._build_having(having_filters, select_fields)

            # 5. Cláusulas GROUP BY e ORDER BY
            group_by_clause = Util._build_group_by(group_by)
            order_by_clause = Util._build_order_by(order_by)

            # Montagem final da query
            query = sql.SQL("""
                SELECT {select} 
                FROM {base_table}
                {joins}
                {where}
                {group_by}
                {having}
                {order_by}
            """).format(
                select=select_clause,
                base_table=base_table,
                joins=sql.SQL(' ').join(join_clauses) if join_clauses else sql.SQL(''),
                where=where_clause,
                group_by=group_by_clause,
                having=having_clause,
                order_by=order_by_clause
            )

            # 6. Execução e retorno
            filter_values.extend(having_values)  # Combina os valores de WHERE e HAVING

            with self.__get_connection().cursor() as cursor:
                cursor.execute(query, filter_values)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

            # Converte as linhas em objetos
            if not rows:
                return None

            result = [Util._row_to_object(base_model, row, columns) for row in rows]

            # Retorna um único objeto se single_result for True ou se houver apenas um resultado
            if single_result or len(result) == 1:
                return result[0] if result else None

            return result

        except psycopg.Error as e:
            # Captura a query que falhou para diagnóstico
            query_str = query.as_string(self.__get_connection()) if locals().get("query") else "Query não gerada"
            logger.error(f"Erro na consulta: {e}\nQuery: {query_str}")
            raise



class QueryBuilder:
    """Constrói consultas de forma intuitiva e orientada a objetos."""
    def __init__(self, model_class):
        self.model = model_class
        self._filters = {}
        self._order_by = []
        self._group_by = []
        self._select = []
        self._joins = []
        self._having = {}
        self._aliases = {}

    def filter(self, *args, **kwargs):
        """Adiciona filtros à consulta (cláusula WHERE)."""
        for condition in args:
            if isinstance(condition, Q):
                self._filters.update(condition.conditions)
        self._filters.update(kwargs)
        return self

    def select(self, *fields):
        """Seleciona campos específicos (colunas regulares, não agregações)."""
        for field in fields:
            self._select.append(field)
        return self

    def order_by(self, *fields):
        """Define a ordenação dos resultados."""
        self._order_by.extend(fields)
        return self

    def annotate(self, **aggregations):
        """Adiciona agregações à consulta."""
        for alias, aggregation in aggregations.items():
            if isinstance(aggregation, Count):
                field = aggregation.field
                self._select.append(f"COUNT({field}) AS {alias}")
                self._aliases[alias] = f"COUNT({field})"
            elif isinstance(aggregation, Avg):
                field = aggregation.field
                self._select.append(f"AVG({field}) AS {alias}")
                self._aliases[alias] = f"AVG({field})"
            elif isinstance(aggregation, Sum):
                field = aggregation.field
                self._select.append(f"SUM({field}) AS {alias}")
                self._aliases[alias] = f"SUM({field})"
            elif isinstance(aggregation, Max):
                field = aggregation.field
                self._select.append(f"MAX({field}) AS {alias}")
                self._aliases[alias] = f"MAX({field})"
            elif isinstance(aggregation, Min):
                field = aggregation.field
                self._select.append(f"MIN({field}) AS {alias}")
                self._aliases[alias] = f"MIN({field})"
            else:
                # Para referências diretas a colunas
                self._select.append(f"{aggregation} AS {alias}")
                self._aliases[alias] = str(aggregation)
        return self

    def group_by(self, *fields):
        """Define o agrupamento dos resultados."""
        self._group_by.extend(fields)
        return self

    def having(self, **filters):
        """Adiciona filtros de agregação (HAVING)."""
        self._having.update(filters)
        return self

    def join(self, related_model):
        """Especifica um relacionamento para incluir na consulta."""
        self._joins.append(related_model)
        return self

    def execute(self):
        """Executa a consulta e retorna os resultados."""
        # Converte os objetos para parâmetros do método execute
        filters = {}
        for field, value in self._filters.items():
            if isinstance(field, F):
                filters[field.field_name] = value
            else:
                filters[field] = value

        # Converte ordenação
        order = [f if isinstance(f, str) else f.field_name for f in self._order_by]

        # Executa a consulta
        return Query().execute(
            self.model,
            where=filters,
            order_by=order,
            group_by=self._group_by,
            having=self._having,
            select=self._select
        )

    def execute_sql(self, query: str, params: List[Any] = None) -> List[Any]:
        """Executa uma consulta SQL no banco de dados com os parâmetros fornecidos."""
        return Query().execute_sql(query, params or [])


# Classes auxiliares
class Sum:
    """Representa uma agregação SUM."""
    def __init__(self, field):
        self.field = field

class Max:
    """Representa uma agregação MAX."""
    def __init__(self, field):
        self.field = field

class Min:
    """Representa uma agregação MIN."""
    def __init__(self, field):
        self.field = field

class Count:
    """Representa uma agregação COUNT."""
    def __init__(self, field='*'):
        self.field = field


class Avg:
    """Representa uma agregação AVG."""
    def __init__(self, field):
        self.field = field


class Q:
    """Representa condições de filtro complexas."""
    def __init__(self, **kwargs):
        self.conditions = kwargs

    def __or__(self, other):
        """Combina condições com OR."""
        return Q(**{f"OR_{k}": v for k, v in {**self.conditions, **other.conditions}.items()})

    def __and__(self, other):
        """Combina condições com AND."""
        return Q(**{f"AND_{k}": v for k, v in {**self.conditions, **other.conditions}.items()})


class F:
    """Representa referências a campos do modelo."""
    def __init__(self, field_name):
        self.field_name = field_name

    def asc(self):
        """Ordenação ascendente."""
        return f"{self.field_name} ASC"

    def desc(self):
        """Ordenação descendente."""
        return f"{self.field_name} DESC"


