import threading
from typing import Any

from jedi.plugins.django import mapping

from arcforge.core.model.field import Field, ValidationError


class Util:

    @staticmethod
    def validationType(model, model_instance):
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
    def _row_to_object(model, row, columns):
        """Mapeia uma linha do banco para uma instância do modelo e seus relacionamentos corretamente."""
        instance = model()
        related_instances = {}

        model_table_name = getattr(model, "_table_name", model.__name__.lower())  # Obtém o nome correto da tabela

        for col, value in zip(columns, row):
            if "." in col:
                table_name, column_name = col.split(".", 1)  # Divide apenas na primeira ocorrência

                if table_name == model_table_name:
                    setattr(instance, column_name, value)
                else:
                    # Verifica se já existe uma instância do modelo relacionado, senão cria um dicionário básico
                    if table_name not in related_instances:
                        related_instances[table_name] = {}

                    related_instances[table_name][column_name] = value  # Armazena os valores temporariamente
            else:
                setattr(instance, col, value)

        # Verifica e instancia objetos relacionados corretamente
        for rel in getattr(model, "_relationships", []):
            related_table = rel["ref_table"]
            related_class = rel["model_class"]
            attr_name = rel["attr_name"]

            if related_table in related_instances:
                related_instance = related_class(**related_instances[related_table])  # Constrói o objeto com os dados
                setattr(instance, attr_name, related_instance)  # Atribui o objeto ao modelo principal

        return instance