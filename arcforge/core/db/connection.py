import psycopg
from psycopg import sql
from contextlib import contextmanager
from typing import Type, Any, List, Dict
from arcforge.core.model.field import Field, ValidationError
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
# Garante que apenas uma instância de DatabaseConnection seja criada.
# -----------------------------------------------------------------------------
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# -----------------------------------------------------------------------------
# Design Pattern: Facade
# A classe DatabaseConnection simplifica o acesso às operações com o banco,
# encapsulando a complexidade da API do psycopg.
# -----------------------------------------------------------------------------
class DatabaseConnection(metaclass=Singleton):
    """Gerencia a conexão com o banco de dados e operações relacionadas."""

    def __init__(self):
        self._conexao = None
        self.set_conexao()

    def set_conexao(self):
        """Estabelece uma conexão com o banco de dados, se ainda não estiver conectada."""
        if self._conexao is None:
            try:
                self._conexao = psycopg.connect(
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

    # -----------------------------------------------------------------------------
    # Design Pattern: Context Manager
    # Garante que o cursor seja fechado corretamente, mesmo em caso de erro.
    # -----------------------------------------------------------------------------
    @contextmanager
    def get_cursor(self):
        """Fornece um cursor gerenciado para operações no banco de dados."""
        cursor = self._conexao.cursor()
        try:
            yield cursor
        except psycopg.Error as e:
            self._conexao.rollback()
            logger.error("Erro durante operação com o cursor. Rollback executado.")
            raise e
        finally:
            cursor.close()

    # -----------------------------------------------------------------------------
    # Design Pattern: Strategy Pattern
    # A validação dos campos é delegada aos métodos de validação de cada Field.
    # -----------------------------------------------------------------------------
    def validationType(self, model, model_instance):
        """
        Valida os tipos dos campos de uma instância do modelo usando a validação
        já implementada nas classes de Field.
        """
        # Itera sobre os atributos definidos na instância (evitando os atributos herdados da classe)
        for attr_name in model_instance.__dict__:
            # Obtém o Field definido na classe, se existir
            field = getattr(model, attr_name, None)
            if isinstance(field, Field):
                value = model_instance.__dict__[attr_name]
                try:
                    field.validate(value)
                except ValidationError as e:
                    raise ValidationError(
                        f"Erro no campo '{attr_name}': {str(e)}",
                        field.field_type,
                        value
                    )

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
            with self.get_cursor() as cursor:
                cursor.execute(create_table_query)
                self._conexao.commit()
                logger.info(f"Tabela {base_model._table_name} criada com sucesso.")
        except psycopg.Error as e:
            logger.error(f"Erro ao criar a tabela {base_model._table_name}: {e}")
            raise

    def save(self, model_instance):
        """Salva (INSERT) a instância no banco de dados."""
        self.validationType(model_instance.__class__, model_instance)
        # Seleciona apenas atributos definidos na instância (exclui atributos não definidos no __dict__)
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
            with self.get_cursor() as cursor:
                cursor.execute(query, values)
                self._conexao.commit()
                model_instance.id = cursor.fetchone()[0]
                logger.info(f"Instância de {model_instance.__class__.__name__} salva com sucesso.")
                return model_instance
        except psycopg.Error as e:
            logger.error(f"Erro ao salvar a instância {model_instance._table_name}: {e}")
            raise

    def update(self, model_instance):
        """Atualiza (UPDATE) a instância no banco de dados."""
        self.validationType(model_instance.__class__, model_instance)
        model_id = getattr(model_instance, "id", None)
        if not model_id:
            raise ValueError("Não é possível realizar o UPDATE sem um ID válido.")

        # Seleciona atributos para atualização (excluindo 'id' e atributos privados)
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
            with self.get_cursor() as cursor:
                cursor.execute(query, values)
                self._conexao.commit()
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
            with self.get_cursor() as cursor:
                cursor.execute(query, (object_id,))
                self._conexao.commit()
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
            with self.get_cursor() as cursor:
                cursor.execute(query, (object_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return self._row_to_object(model_class, row, columns)
                return None
        except psycopg.Error as e:
            logger.error(f"Erro ao buscar {model_class.__name__} com ID {object_id}: {e}")
            raise

    def query_sql(self, query: str, params: List[Any]) -> List[Any]:
        """Executa uma consulta SQL personalizada."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except psycopg.Error as e:
            logger.error(f"Erro ao executar a consulta: {e}")
            raise

    def query(self, base_model, **filters) -> List[Any]:
        """
        Executa uma consulta no banco de dados com base nos filtros e inferindo os joins automaticamente.

        Design Pattern: Repository Pattern – encapsula a lógica de acesso e transformação
        dos dados, retornando objetos do domínio.
        """
        try:
            base_query = sql.SQL("SELECT {base_table}.* FROM {base_table}").format(
                base_table=sql.Identifier(base_model._table_name)
            )

            join_clauses = []
            relationships = getattr(base_model, "_relationships", [])
            joined_tables = {base_model._table_name: True}

            for rel in relationships:
                ref_table = rel["ref_table"]
                base_column = rel["field_name"]  # Agora, field_name já inclui o sufixo _id
                ref_field = "id"  # Campo padrão de referência
                if ref_table not in joined_tables:
                    join_clause = sql.SQL(
                        " JOIN {ref_table} ON {base_table}.{base_column} = {ref_table}.{ref_field}"
                    ).format(
                        ref_table=sql.Identifier(ref_table),
                        base_table=sql.Identifier(base_model._table_name),
                        base_column=sql.Identifier(base_column),
                        ref_field=sql.Identifier(ref_field)
                    )
                    join_clauses.append(join_clause)
                    joined_tables[ref_table] = True

            filter_clauses = []
            filter_values = []
            for column, value in filters.items():
                # Suporte a filtros usando "tabela_coluna" ou "tabela.coluna"
                if "_" in column and "." not in column:
                    table, column_name = column.split("_", 1)
                    column = f"{table}.{column_name}"
                if "." in column:
                    table, column_name = column.split(".")
                    filter_clauses.append(sql.SQL("{table}.{column} = %s").format(
                        table=sql.Identifier(table),
                        column=sql.Identifier(column_name)
                    ))
                else:
                    filter_clauses.append(sql.SQL("{table}.{column} = %s").format(
                        table=sql.Identifier(base_model._table_name),
                        column=sql.Identifier(column)
                    ))
                filter_values.append(value)

            where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(filter_clauses) if filter_clauses else sql.SQL("")
            full_query = base_query + sql.SQL(" ").join(join_clauses) + where_clause

            with self.get_cursor() as cursor:
                cursor.execute(full_query, filter_values)
                rows = cursor.fetchall()
                # Utiliza cursor.description para obter os nomes das colunas
                columns = [desc[0] for desc in cursor.description]
                return [self._row_to_object(base_model, row, columns) for row in rows]
        except psycopg.Error as e:
            logger.error(f"Erro ao executar a consulta: {e}")
            raise

    # -----------------------------------------------------------------------------
    # Design Pattern: Data Mapper
    # Mapeia os dados retornados do banco para instâncias do modelo.
    # -----------------------------------------------------------------------------
    def _row_to_object(self, model, row, columns) -> Any:
        """Mapeia uma linha do banco para uma instância do modelo e seus relacionamentos corretamente."""
        instance = model()
        related_instances = {}  # Armazena instâncias dos modelos relacionados

        for col, value in zip(columns, row):
            if "." in col:
                table_name, column_name = col.split(".")
                if table_name == model._table_name:
                    setattr(instance, column_name, value)
                else:
                    # Criar instância do modelo relacionado, se ainda não existir
                    if table_name not in related_instances:
                        related_model = self._get_model_by_table(table_name)
                        if related_model:
                            related_instances[table_name] = related_model()

                    if related_model:
                        setattr(related_instances[table_name], column_name, value)
            else:
                setattr(instance, col, value)

        # Substituir referências ManyToOne pelo objeto real
        for rel in getattr(model, "_relationships", []):
            related_instance = related_instances.get(rel["ref_table"])
            if related_instance:
                setattr(instance, rel["attr_name"], related_instance)  # `attr_name` é o nome real do campo

        return instance


    def _get_model_by_table(self, table_name):
        """
        Retorna a classe do modelo associada a uma tabela.
        """
        return mapping.get(table_name, None)



    # Métodos antigos de transformação foram removidos por questões de performance.

    # -----------------------------------------------------------------------------
    # Atualização na criação dos metadados de relacionamentos:
    # Quando um relacionamento é definido, o campo na tabela é gerado com o sufixo "_id".
    # -----------------------------------------------------------------------------
    def _store_relationship_metadata(self, attr_name: str, relationship: Field) -> None:
        """
        Armazena os metadados dos relacionamentos.
        ATENÇÃO: O nome do campo é armazenado com o sufixo "_id" para refletir
        a definição SQL gerada em _generate_fields.
        """
        # Aqui, 'relationship' é uma instância de Relationship
        # Altere o nome do campo para incluir o sufixo "_id"
        meta_field_name = f"{attr_name}_id"
        if hasattr(relationship, "ref_column"):
            ref_column = relationship.ref_column
        else:
            ref_column = "id"
        # Armazena os metadados
        if not hasattr(relationship.__class__, "_relationships"):
            relationship.__class__._relationships = []
        # Para esta implementação, assume-se que a classe Model gerencia os relacionamentos
        # através do método _store_relationship_metadata já definido na classe Model.
        # Assim, aqui não é necessário reimplementar, pois o método _generate_fields (na classe Model)
        # deverá chamar a versão correta que já inclui o sufixo "_id".
        pass  # Esse método está agora implementado na classe Model (ver model.py)


