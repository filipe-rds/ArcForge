from typing import List
from abc import ABC


class DAO(ABC):

    _model = None  # Propriedade de classe que será definida pela subclasse

    def __init__(self):
        from arcforge.core.model.model import Model
        from .query import Query

        if self._model is None:
            raise NotImplementedError("A classe concreta deve definir o atributo _model")

        self._query = Query()

        if not issubclass(self._model, Model):
            raise TypeError(f"A classe {self._model.__name__} deve herdar da classe Model")

        if not self.table_exists():
            self.create_table()

    def table_exists(self) -> bool:
        return self._query.table_exists(self._model._table_name)

    def create_table(self):
        self._query.create_table(self._model)

    def delete_table(self):
        self._query.delete_table(self._model)

    def save(self, model_instance) -> object:
        if not isinstance(model_instance, self._model):
            raise TypeError(f"Objeto inválido para este DAO. Esperado: {self._model.__name__}")

        return self._query.save(model_instance)

    def update(self, model_instance) -> object:
        if not isinstance(model_instance, self._model):
            raise TypeError(f"Objeto inválido para este DAO. Esperado: {self._model.__name__}")

        return self._query.update(model_instance)

    def read(self, object_id) -> object:
        return self._query.read(self._model, object_id)

    def delete(self, object_id):
        self._query.delete(self._model, object_id)

    def find_all(self) -> List[object]:
        return self._query.find_all(self._model)