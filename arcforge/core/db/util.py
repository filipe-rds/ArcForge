from psycopg import sql
from typing import List, Any

class Util:

    @staticmethod
    def validationType(model, model_instance):
        from arcforge.core.model.field import Field, ValidationError
        """
        Valida os tipos dos campos de uma instância do modelo usando a validação
        já implementada nas classes de Field.
        """
        for attr_name in model_instance.__dict__:
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

    @staticmethod
    def _row_to_object(model, row, columns) -> Any:
        """Mapeia uma linha do banco para uma instância do modelo e seus relacionamentos corretamente."""
        instance = model()
        related_instances = {}

        for col, value in zip(columns, row):
            if "." in col:
                table_name, column_name = col.split(".", 1)
                if table_name == model._table_name:
                    setattr(instance, column_name, value)
                else:
                    if table_name not in related_instances:
                        related_instances[table_name] = {}

                    related_instances[table_name][column_name] = value
            else:
                setattr(instance, col, value)

        for rel in getattr(model, "_relationships", []):
            related_table = rel.get("ref_table")
            related_class = rel.get("model_class")
            attr_name = rel.get("attr_name")

            if related_table and related_class and related_table in related_instances:
                related_instance = related_class(**related_instances[related_table])
                setattr(instance, attr_name, related_instance)

        return instance
    @staticmethod
    def _generate_joins(base_model, base_table) -> List[sql.Composable]:
        """
        Gera automaticamente as cláusulas JOIN com base nas relações do modelo.

        Args:
            base_model: Classe do modelo base.
            base_table: Identificador SQL da tabela base.

        Returns:
            List[sql.Composable]: Lista de cláusulas JOIN.
        """
        join_clauses = []
        relationships = getattr(base_model, "_relationships", [])
        joined_tables = {base_model._table_name: True}  # Tabelas já incluídas

        for rel in relationships:
            ref_table = rel["ref_table"]
            base_column = rel["field_name"]
            ref_field = rel.get("ref_field", "id")

            if ref_table not in joined_tables:
                join_clause = sql.SQL("JOIN {ref_table} ON {base_table}.{base_column} = {ref_table}.{ref_field}").format(
                    ref_table=sql.Identifier(ref_table),
                    base_table=base_table,
                    base_column=sql.Identifier(base_column),
                    ref_field=sql.Identifier(ref_field))
                join_clauses.append(join_clause)
                joined_tables[ref_table] = True

        return join_clauses
    @staticmethod
    def _build_group_by(group_by) -> sql.Composable:
        """
        Constrói a cláusula GROUP BY.

        Args:
            group_by: Coluna(s) para agrupamento.

        Returns:
            sql.Composable: Cláusula GROUP BY.
        """
        if not group_by:
            return sql.SQL('')

        columns = [group_by] if isinstance(group_by, str) else group_by
        group_items = []

        for col in columns:
            # Verifica se temos uma referência de tabela.coluna
            if '.' in col:
                table, column = col.split('.', 1)
                group_items.append(
                    sql.SQL("{}.{}").format(
                        sql.Identifier(table),
                        sql.Identifier(column)
                    )
                )
            else:
                # Coluna simples sem qualificação de tabela
                group_items.append(sql.Identifier(col))

        return sql.SQL(' GROUP BY ') + sql.SQL(', ').join(group_items)
    @staticmethod
    def _build_order_by(order_by) -> sql.Composable:
        """
        Constrói a cláusula ORDER BY.

        Args:
            order_by: Coluna(s) para ordenação.

        Returns:
            sql.Composable: Cláusula ORDER BY.
        """
        if not order_by:
            return sql.SQL('')

        orders = [order_by] if isinstance(order_by, str) else order_by
        clauses = []

        for item in orders:
            parts = item.strip().split()
            column_part = parts[0]
            direction = parts[1].upper() if len(parts) > 1 and parts[1].upper() in ('ASC', 'DESC') else ''

            # Verifica se é um alias ou campo calculado
            if any(char in column_part for char in ['(', ')', ' ']):
                # Usa diretamente o alias/expressão sem qualificação e sem identificador
                clause = sql.SQL(column_part)
            elif '.' in column_part:
                # Qualificação normal para campos da tabela
                table, column = column_part.split(".", 1)
                clause = sql.SQL("{}.{}").format(
                    sql.Identifier(table),
                    sql.Identifier(column)
                )
            else:
                # Coluna simples
                clause = sql.Identifier(column_part)

            if direction:
                clause = sql.SQL("{} {}").format(clause, sql.SQL(direction))

            clauses.append(clause)

        return sql.SQL(' ORDER BY ') + sql.SQL(', ').join(clauses)
    @staticmethod
    def _build_having(having_filters, select_fields=None) -> (sql.Composable, list):
        """
        Constrói a cláusula HAVING com suporte a aliases de agregação.

        Args:
            having_filters: Filtros para a cláusula HAVING.
            select_fields: Lista de campos selecionados para mapear os aliases.

        Returns:
            Tuple[sql.Composable, list]: Cláusula HAVING e valores para os parâmetros.
        """
        if not having_filters:
            return sql.SQL(""), []

        # Cria um mapa de alias -> expressão completa
        alias_map = {}
        if select_fields:
            for field in select_fields:
                if ' AS ' in field.upper():
                    expression, alias = field.split(' AS ', 1)
                    alias_map[alias.strip().lower()] = expression.strip()

        having_clauses = []
        having_values = []

        for key, value in having_filters.items():
            if "__" in key:
                field, operator = key.split("__", 1)
                operator = operator.lower()
            else:
                field, operator = key, "eq"

            # Mapeia operadores
            sql_operator = {
                "eq": "=", "gt": ">", "lt": "<", "gte": ">=", "lte": "<="
            }.get(operator, "=")

            # Verifica se o campo é um alias e substitui pela expressão completa
            field_lower = field.lower()
            if field_lower in alias_map:
                # Usa a expressão completa em vez do alias
                field_expression = alias_map[field_lower]
            else:
                # Mantém o campo original
                field_expression = field

            # Constrói cláusula HAVING usando a expressão completa
            having_clauses.append(sql.SQL("{} {} %s").format(
                sql.SQL(field_expression),
                sql.SQL(sql_operator)
            ))
            having_values.append(value)

        return sql.SQL(" HAVING ") + sql.SQL(" AND ").join(having_clauses), having_values
    @staticmethod
    def _parse_column_reference(base_model, column: str) -> (str, str):
        """
        Extrai a tabela e a coluna de uma referência no formato "tabela.coluna" ou apenas "coluna".

        Args:
            base_model: Classe do modelo base.
            column: Referência da coluna.

        Returns:
            Tuple[str, str]: Tabela e coluna. Se a coluna for uma expressão SQL, a tabela será None.
        """
        if "." in column:
            return column.split(".", 1)
        elif any(op in column for op in ["(", ")"]):  # Expressão SQL (ex: COUNT(*))
            return None, column
        return base_model._table_name, column

