import psycopg2
from psycopg2 import sql
from arcforge.core.db.config import *


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados e a criação de tabelas."""
    def __init__(self):
        self._conexao = None

    def set_conexao(self):
        """Estabelece uma conexão com o banco de dados, se ainda não estiver conectada."""
        if self._conexao is None:
            self._conexao = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
            )

    def get_conexao(self):
        """Retorna a conexão ativa com o banco de dados."""
        self.set_conexao()
        return self._conexao

    def create_table(self, base_model):
        """Cria a tabela no banco de dados com base no modelo fornecido."""
        self.set_conexao()

        fields = base_model._generate_fields()
        try:
            create_table_query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {table} (
                    {fields}
                );
            """).format(
                table=sql.Identifier(base_model._table_name),
                fields=sql.SQL(fields)
            )

            with self._conexao.cursor() as cursor:
                cursor.execute(create_table_query)
                self._conexao.commit()

            # Configurar relacionamentos Many-to-Many
            #base_model._create_relationships()
        except psycopg2.Error as e:
            print(f"Erro ao criar a tabela {base_model._table_name}: {e}")



    def save(self, model_instance):
            """Salva ou atualiza a instância no banco de dados."""
            fields = []
            values = []
            placeholders = []

            # Extrai os atributos e valores do modelo
            for attr, value in model_instance.__dict__.items():
                if attr in model_instance.__class__.__dict__:
                    fields.append(attr)
                    values.append(value)
                    placeholders.append(sql.Placeholder())

            query = sql.SQL("""
                INSERT INTO {table} ({fields})
                VALUES ({placeholders})
            """).format(
                table=sql.Identifier(model_instance._table_name),
                fields=sql.SQL(", ").join(map(sql.Identifier, fields)),
                placeholders=sql.SQL(", ").join(placeholders)
            )

            try:
                with self._conexao.cursor() as cursor:
                    cursor.execute(query, values)
                    self._conexao.commit()
            except psycopg2.Error as e:
                print(f"Erro ao salvar a instância {model_instance._table_name}: {e}")