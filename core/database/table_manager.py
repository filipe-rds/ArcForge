from .query_builder import QueryBuilder
from .. import db  # Importando a variável global de conexão db do __init__.py


class TableManager:
    """Classe para gerenciar migrações do banco de dados."""

    def __init__(self):
        self.db = db

    def _table_exists(self, table_name):
        """Verifica se uma tabela existe no banco de dados."""
        query = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = '{table_name}'
        );
        """
        result = self.db.execute(query)
        return result.fetchone()[0]

    def _column_exists(self, table_name, column_name):
        """Verifica se uma coluna existe em uma tabela."""
        query = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = '{table_name}' AND column_name = '{column_name}'
        );
        """
        result = self.db.execute(query)
        return result.fetchone()[0]

    def create_table(self, table_name, columns):
        """Cria uma nova tabela no banco de dados."""
        if not self._table_exists(table_name):
            query_builder = QueryBuilder(table_name)
            create_table_query = query_builder.create_table(columns)
            self.db.execute(create_table_query)
            print(f"Tabela {table_name} criada com sucesso.")
        else:
            print(f"Tabela {table_name} já existe, nenhuma ação foi realizada.")

    def drop_table(self, table_name):
        """Remove uma tabela do banco de dados."""
        if self._table_exists(table_name):
            query_builder = QueryBuilder(table_name)
            drop_table_query = query_builder.drop_table()
            self.db.execute(drop_table_query)
            print(f"Tabela {table_name} removida com sucesso.")
        else:
            print(f"Tabela {table_name} não existe, nenhuma ação foi realizada.")

    def update_table(self, table_name, fields):
        """Atualiza uma tabela existente (adiciona colunas novas)."""
        if self._table_exists(table_name):
            for field_name, field_type in fields.items():
                if not self._column_exists(table_name, field_name):
                    # Se a coluna não existir, adiciona
                    self.add_column(table_name, field_name, field_type)
        else:
            print(f"Tabela {table_name} não existe, nenhuma ação foi realizada.")

    def add_column(self, table_name, column_name, column_definition):
        """Adiciona uma nova coluna a uma tabela existente."""
        if not self._column_exists(table_name, column_name):
            query_builder = QueryBuilder(table_name)
            add_column_query = query_builder.add_column(column_name, column_definition)
            self.db.execute(add_column_query)
            print(f"Coluna {column_name} adicionada à tabela {table_name} com sucesso.")
        else:
            print(f"Coluna {column_name} já existe na tabela {table_name}, nenhuma ação foi realizada.")

    def drop_column(self, table_name, column_name):
        """Remove uma coluna de uma tabela existente."""
        if self._column_exists(table_name, column_name):
            query_builder = QueryBuilder(table_name)
            drop_column_query = query_builder.drop_column(column_name)
            self.db.execute(drop_column_query)
            print(f"Coluna {column_name} removida da tabela {table_name} com sucesso.")
        else:
            print(f"Coluna {column_name} não existe na tabela {table_name}, nenhuma ação foi realizada.")

    def rename_table(self, old_table_name, new_table_name):
        """Renomeia uma tabela existente."""
        if self._table_exists(old_table_name):
            query_builder = QueryBuilder(old_table_name)
            rename_table_query = query_builder.rename_table(new_table_name)
            self.db.execute(rename_table_query)
            print(f"Tabela {old_table_name} renomeada para {new_table_name} com sucesso.")
        else:
            print(f"Tabela {old_table_name} não existe, nenhuma ação foi realizada.")

    def rename_column(self, table_name, old_column_name, new_column_name):
        """Renomeia uma coluna em uma tabela existente."""
        if self._column_exists(table_name, old_column_name):
            query_builder = QueryBuilder(table_name)
            rename_column_query = query_builder.rename_column(old_column_name, new_column_name)
            self.db.execute(rename_column_query)
            print(f"Coluna {old_column_name} renomeada para {new_column_name} na tabela {table_name}.")
        else:
            print(f"Coluna {old_column_name} não existe na tabela {table_name}, nenhuma ação foi realizada.")

    def migrate(self, model):
        """Realiza migrações baseadas nas mudanças do modelo."""
        table_name = model._table_name
        fields = {field_name: field.field_type for field_name, field in model._fields.items()}

        if not self._table_exists(table_name):
            # Se a tabela não existir, cria a tabela do zero
            self.create_table(table_name, fields)
        else:
            # Caso a tabela já exista, verifica se existem alterações
            self.update_table(table_name, fields)
