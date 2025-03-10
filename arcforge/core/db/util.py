import threading

from jedi.plugins.django import mapping

from arcforge.core.model.field import Field, ValidationError


class Singleton(type):
    _instances = {}
    _lock = threading.Lock()  # Lock para evitar problemas em ambientes multithread

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Util(metaclass=Singleton):

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