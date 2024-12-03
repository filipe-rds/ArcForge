import psycopg2
from psycopg2 import sql
from config import *
from atributos import *


class ForeignKey:
    """Representa uma chave estrangeira."""

    def __init__(self, related_class, on_delete="CASCADE"):
        self.related_class = related_class
        self.on_delete = on_delete

    def to_sql(self, related_table_name):
        return f"INTEGER REFERENCES {related_table_name}(id) ON DELETE {self.on_delete}"


class BaseModel:
    """Classe base para modelos."""
    # A classe BaseModel serve como base para outros modelos que representam entidades no banco de dados.
    
    _conexao = None  # A variável de classe _conexao armazenará a conexão com o banco de dados.
    _table_name = None  # A variável de classe _table_name armazenará o nome da tabela do banco de dados.
    _relationships = {}  # A variável de classe _relationships armazenará os relacionamentos entre tabelas (chaves estrangeiras).

    def __init__(self, **kwargs):
        # O construtor __init__ recebe parâmetros dinâmicos **kwargs, que permitem passar qualquer número de argumentos nomeados.
        for field, value in kwargs.items():
            # Este laço percorre todos os campos e valores passados no dicionário kwargs.
            setattr(self, field, value)
            # Para cada campo e valor, a função setattr define um atributo na instância do modelo (self), atribuindo o valor correspondente.

    @classmethod
    def set_conexao(cls):
        if cls._conexao is None:
            cls._conexao = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
            )

    # Método para criar a tabela
    @classmethod
    def create_table(cls):
        """Cria a tabela correspondente à classe."""
        cls.set_conexao()
        fields = cls._generate_fields()
        try:
            create_table_query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {table} (
                    {fields}
                );
            """).format(
                table=sql.Identifier(cls._table_name),
                fields=sql.SQL(fields)
            )
            with cls._conexao.cursor() as cursor:
                cursor.execute(create_table_query)
                cls._conexao.commit()

            # Configurar relacionamentos
            cls._create_relationships()
        except psycopg2.Error as e:
            print(e)

    # Método que vai gerar a string com os campos da tabela, que será usado no método create_table
    @classmethod
    def _generate_fields(cls):
        fields = []
        #cls.__dict__.items() retorna a variável e o valor dela
        for attr, field in cls.__dict__.items():
            #Se o campo for uma instância de Field, ele adiciona o campo na lista de campos
            if isinstance(field, Field):
                #field.to_sql() retorna o campo em formato SQL
                fields.append(f"{attr} {field.to_sql()}")
            elif isinstance(field, ForeignKey):
                related_table_name = field.related_class._table_name
                fields.append(f"{attr}_id {field.to_sql(related_table_name)}")
        return ", ".join(fields)

    @classmethod
    def _create_relationships(cls):
        """Cria tabelas para relacionamentos Many-to-Many."""
        for related_table, config in cls._relationships.items():
            if config["type"] == "ManyToMany":
                join_table = f"{cls._table_name}_{related_table}"
                try:
                    create_table_query = sql.SQL("""
                        CREATE TABLE IF NOT EXISTS {join_table} (
                            {left_table}_id INTEGER REFERENCES {left_table}(id),
                            {right_table}_id INTEGER REFERENCES {right_table}(id),
                            PRIMARY KEY ({left_table}_id, {right_table}_id)
                        );
                    """).format(
                        join_table=sql.Identifier(join_table),
                        left_table=sql.Identifier(cls._table_name),
                        right_table=sql.Identifier(related_table),
                    )
                    with cls._conexao.cursor() as cursor:
                        cursor.execute(create_table_query)
                        cls._conexao.commit()
                except psycopg2.Error as e:
                    raise RuntimeError(
                        f"Erro ao criar relacionamento Many-to-Many com '{related_table}'.") from e

    # Método para salvar os dados

    # sql.Placeholder(): Para substituir valores.
    # .Identifier(): Para substituir nomes de colunas ou tabelas.
    # sql.SQL(): Para montar a query de forma segura e dinâmica.

    def save(self):
        """Salva ou atualiza a instância no banco de dados."""
        fields = []
        values = []
        placeholders = []

        # Não inclui o campo 'id' no INSERT, pois é auto-incrementado no PostgreSQL
        for attr, value in self.__dict__.items():
            if attr != 'id' and attr in self.__class__.__dict__:
                fields.append(attr) # Adiciona o nome do campo
                values.append(value) # Adiciona o valor do campo
                placeholders.append(sql.Placeholder()) # Adiciona um placeholder

        query = sql.SQL("""
            INSERT INTO {table} ({fields})
            VALUES ({placeholders})
        """).format(
            table=sql.Identifier(self._table_name),
            fields=sql.SQL(", ").join(map(sql.Identifier, fields)),
            placeholders=sql.SQL(", ").join(placeholders)
        )

        try:
            with self._conexao.cursor() as cursor:
                cursor.execute(query, values)
                self._conexao.commit()
        except psycopg2.Error as e:
            print(e)

    @classmethod
    def add_relationship(cls, related_class, rel_type):
        """Adiciona configuração de relacionamento."""
        cls._relationships[related_class._table_name] = {
            "related_class": related_class, "type": rel_type}

    @classmethod
    def filter(cls, **conditions):
        """Filtra os registros com base nas condições fornecidas."""
        cls.set_conexao()
        where_clauses = []
        values = []

        for field, value in conditions.items():
            if hasattr(cls, field):
                where_clauses.append(f"{field} = %s")
                values.append(value)

        if not where_clauses:
            raise ValueError("Nenhuma condição foi fornecida para o filtro.")

        where_clause = " AND ".join(where_clauses)

        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE {where_clause}
        """).format(
            table=sql.Identifier(cls._table_name),
            where_clause=sql.SQL(where_clause)
        )

        try:
            with cls._conexao.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchall()
                return result  # Retorna os registros filtrados
        except psycopg2.Error as e:
            print(e)
            raise RuntimeError(f"Erro ao realizar o filtro na tabela '{cls._table_name}'.") from e


# Decorators para Relacionamentos

def OneToOne(related_class, on_delete="CASCADE"):
    """Define um relacionamento One-to-One."""
    def decorator(cls):
        cls._relationships[related_class._table_name] = {
            "type": "OneToOne",
            "related_class": related_class,
            "on_delete": on_delete,
        }
        setattr(cls, f"{related_class._table_name}_id",
                ForeignKey(related_class, on_delete))
        return cls
    return decorator


def ManyToOne(related_class, on_delete="CASCADE"):
    """Define um relacionamento Many-to-One."""
    def decorator(cls):
        cls._relationships[related_class._table_name] = {
            "type": "ManyToOne",
            "related_class": related_class,
            "on_delete": on_delete,
        }
        setattr(cls, f"{related_class._table_name}_id",
                ForeignKey(related_class, on_delete))
        return cls
    return decorator


def OneToMany(related_class):
    """Define um relacionamento One-to-Many."""
    def decorator(cls):
        cls._relationships[related_class._table_name] = {
            "type": "OneToMany",
            "related_class": related_class,
        }
        return cls
    return decorator


def ManyToMany(related_class):
    """Define um relacionamento Many-to-Many."""
    def decorator(cls):
        cls.add_relationship(related_class, "ManyToMany")
        return cls
    return decorator
