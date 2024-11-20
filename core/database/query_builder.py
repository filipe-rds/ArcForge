# core/database/query_builder.py

class QueryBuilder:
    """Classe para construir queries SQL dinâmicas."""

    def __init__(self, table_name):
        self.table_name = table_name

    def create_table(self, columns: dict):
        """Gera uma query SQL para criação de uma tabela."""
        column_defs = []
        for column_name, column_definition in columns.items():
            column_defs.append(f"{column_name} {column_definition}")
        columns_str = ", ".join(column_defs)
        return f"CREATE TABLE IF NOT EXISTS {self.table_name} ({columns_str});"

    def add_column(self, column_name: str, column_definition: str):
        """Gera a query SQL para adicionar uma nova coluna a uma tabela."""
        return f"ALTER TABLE {self.table_name} ADD COLUMN {column_name} {column_definition};"

    def drop_table(self):
        """Gera a query SQL para remover uma tabela."""
        return f"DROP TABLE IF EXISTS {self.table_name};"

    def drop_column(self, column_name: str):
        """Gera a query SQL para remover uma coluna de uma tabela."""
        return f"ALTER TABLE {self.table_name} DROP COLUMN IF EXISTS {column_name};"

    def rename_table(self, new_table_name: str):
        """Gera a query SQL para renomear uma tabela."""
        return f"ALTER TABLE {self.table_name} RENAME TO {new_table_name};"

    def rename_column(self, old_column_name: str, new_column_name: str):
        """Gera a query SQL para renomear uma coluna."""
        return f"ALTER TABLE {self.table_name} RENAME COLUMN {old_column_name} TO {new_column_name};"

    def insert(self, data: dict):
        """Gera uma query SQL para inserir dados na tabela."""
        columns = ", ".join(data.keys())
        values = ", ".join([f"'{value}'" for value in data.values()])
        return f"INSERT INTO {self.table_name} ({columns}) VALUES ({values});"

    def update(self, data: dict, where: dict):
        """Gera uma query SQL para atualizar dados na tabela."""
        set_clause = ", ".join([f"{key} = '{value}'" for key, value in data.items()])
        where_clause = " AND ".join([f"{key} = '{value}'" for key, value in where.items()])
        return f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause};"

    def select(self, columns: list = ["*"], where: dict = None, order_by: str = None, limit: int = None):
        """Gera uma query SQL para selecionar dados da tabela com opções dinâmicas."""
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {self.table_name}"

        if where:
            where_clause = " AND ".join([f"{key} = '{value}'" for key, value in where.items()])
            query += f" WHERE {where_clause}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        return query + ";"

    def delete(self, where: dict):
        """Gera uma query SQL para excluir dados de uma tabela."""
        where_clause = " AND ".join([f"{key} = '{value}'" for key, value in where.items()])
        return f"DELETE FROM {self.table_name} WHERE {where_clause};"

    def create_index(self, index_name: str, columns: list):
        """Gera uma query SQL para criar um índice em uma tabela."""
        columns_str = ", ".join(columns)
        return f"CREATE INDEX IF NOT EXISTS {index_name} ON {self.table_name} ({columns_str});"

    def alter_column(self, column_name: str, new_definition: str):
        """Gera uma query SQL para alterar a definição de uma coluna existente."""
        return f"ALTER TABLE {self.table_name} ALTER COLUMN {column_name} SET DATA TYPE {new_definition};"

    def drop_index(self, index_name: str):
        """Gera uma query SQL para remover um índice de uma tabela."""
        return f"DROP INDEX IF EXISTS {index_name};"
