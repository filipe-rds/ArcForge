from .. import db
from core.database.table_manager import TableManager
from core.models.fields import *


class Table:
    """Classe usada para definir uma tabela no banco de dados."""

    def __init__(self, name=None):
        self.name = name  # Nome da tabela. Se não fornecido, será o nome da classe em minúsculas.

    def __call__(self, cls):
        """Aplica a anotação na classe."""
        cls._table_name = self.name or cls.__name__.lower()  # Usa o nome da classe como padrão.
        return cls


class ModelMeta(type):
    """Metaclasse para modelos, gerencia os campos e tipos."""

    def __new__(cls, name, bases, attrs):
        fields = {key: value for key, value in attrs.items() if isinstance(value, Field)}
        attrs['_fields'] = fields
        return super().__new__(cls, name, bases, attrs)


class BaseModel(metaclass=ModelMeta):
    """Modelo base para todos os modelos de domínio."""

    @classmethod
    def create_table(cls):
        """Cria a tabela no banco de dados a partir do modelo."""
        table_name = getattr(cls, '_table_name', cls.__name__.lower())
        table_manager = TableManager()
        columns = {field_name: field.field_type for field_name, field in cls._fields.items()}

        # Adiciona restrições de chave estrangeira
        for field_name, field in cls._fields.items():
            if isinstance(field, ForeignKey):
                columns[field_name] = f"{field.field_type} REFERENCES {field.ref_table}({field.ref_column})"

        table_manager.create_table(table_name, columns)

    @classmethod
    def migrate(cls):
        """Executa as migrações para a criação ou atualização da tabela."""
        table_manager = TableManager()
        table_manager.migrate(cls)

    def save(self):
        """Salva o objeto no banco de dados."""
        table_name = getattr(self.__class__, '_table_name', self.__class__.__name__.lower())
        fields = self._fields.keys()
        values = {field: getattr(self, field, None) for field in fields}

        # Monta a query de inserção diretamente.
        columns = ", ".join(values.keys())
        placeholders = ", ".join([f"%({field})s" for field in values.keys()])
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id"

        # Executa a query e atualiza o ID do objeto.
        result = db.execute(insert_query, values).fetchone()
        self.id = result[0] if result else None
        print(f"Registro inserido na tabela {table_name} com ID {self.id}.")

    def update(self):
        """Atualiza os dados do objeto no banco de dados."""
        table_name = getattr(self.__class__, '_table_name', self.__class__.__name__.lower())
        fields = {field: getattr(self, field, None) for field in self._fields.keys() if field != "id"}
        updates = ", ".join([f"{key} = %({key})s" for key in fields.keys()])
        update_query = f"UPDATE {table_name} SET {updates} WHERE id = %(id)s"

        # Adiciona o ID para a cláusula WHERE.
        fields["id"] = self.id
        db.execute(update_query, fields)
        print(f"Registro com ID {self.id} atualizado na tabela {table_name}.")

    def delete(self):
        """Exclui o registro do banco de dados."""
        table_name = getattr(self.__class__, '_table_name', self.__class__.__name__.lower())
        delete_query = f"DELETE FROM {table_name} WHERE id = %(id)s"

        db.execute(delete_query, {"id": self.id})
        print(f"Registro com ID {self.id} excluído da tabela {table_name}.")

    @classmethod
    def all(cls):
        """Recupera todos os registros da tabela."""
        table_name = getattr(cls, '_table_name', cls.__name__.lower())
        query = f"SELECT * FROM {table_name}"
        results = db.execute(query).fetchall()

        print(f"{len(results)} registros encontrados na tabela {table_name}.")
        return [cls._map_to_instance(result) for result in results]

    @classmethod
    def find(cls, **filters):
        """Recupera registros filtrados por campos específicos."""
        table_name = getattr(cls, '_table_name', cls.__name__.lower())
        where_clause = " AND ".join([f"{key} = %({key})s" for key in filters.keys()])
        query = f"SELECT * FROM {table_name} WHERE {where_clause}"
        results = db.execute(query, filters).fetchall()

        print(f"{len(results)} registros encontrados na tabela {table_name} com os filtros fornecidos.")
        return [cls._map_to_instance(result) for result in results]

    @classmethod
    def find_one(cls, **filters):
        """Recupera um único registro filtrado por campos específicos."""
        table_name = getattr(cls, '_table_name', cls.__name__.lower())
        where_clause = " AND ".join([f"{key} = %({key})s" for key in filters.keys()])
        query = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT 1"
        result = db.execute(query, filters).fetchone()

        if result:
            print(f"Registro encontrado na tabela {table_name}.")
            return cls._map_to_instance(result)
        else:
            print(f"Nenhum registro encontrado na tabela {table_name} com os filtros fornecidos.")
            return None

    @classmethod
    def _map_to_instance(cls, row):
        """Mapeia um registro do banco de dados para uma instância do modelo."""
        instance = cls()
        for field_name, value in row.items():
            setattr(instance, field_name, value)
        return instance
