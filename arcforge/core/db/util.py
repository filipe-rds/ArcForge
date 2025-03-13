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
