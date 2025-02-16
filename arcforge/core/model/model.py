from typing import Dict, List, Any

from arcforge.core.model.field import *
from arcforge.core.model.relationships import *
from arcforge.core.db.connection import *

from arcforge.core.model.field import __all__ as fields_all
from arcforge.core.model.relationships import __all__ as relationships_all
from arcforge.core.db.connection import __all__ as connection_all

# -----------------------------------------------------------------------------
# Padrão de Projeto: Active Record
# Cada classe derivada de Model representa uma tabela no banco de dados e
# suas instâncias representam registros dessa tabela.
#
# Padrão de Projeto: Template Method (usado em __init_subclass__)
# Garante que cada subclasse tenha sua própria lista de relacionamentos.
# -----------------------------------------------------------------------------

class Model:
    """Classe base para modelos com gerenciamento automático de campos e relacionamentos.

    Padrão: Active Record - cada instância representa uma linha da tabela e possui métodos
    para persistência e manipulação dos dados.
    """
    @classmethod
    def Table(cls, table_name: str):
        """Decorator para definir o nome da tabela da classe."""
        def wrapper(subclass):
            subclass._table_name = table_name
            return subclass
        return wrapper

    def __init_subclass__(cls, **kwargs):
        # Template Method: Inicialização das subclasses para garantir que cada uma possua sua própria lista de relacionamentos.
        super().__init_subclass__(**kwargs)
        cls._relationships = []  # Cada subclasse terá sua própria lista de relacionamentos

    def __init__(self, **kwargs):
        self._validate_fields(kwargs)
        self._process_relationships(kwargs)
        for field, value in kwargs.items():
            setattr(self, field, value)

    def _process_relationships(self, kwargs: Dict) -> None:
        """Processa objetos passados em relacionamentos.

        Padrão: Strategy Pattern - a estratégia para processar relacionamentos pode ser personalizada.
        """
        # Itera sobre uma cópia dos itens para evitar modificar o dicionário durante a iteração
        for attr_name, value in list(kwargs.items()):
            if attr_name in self.__class__.__dict__:
                field = self.__class__.__dict__[attr_name]
                if isinstance(field, Relationship):
                    # Se o valor for um objeto, extrai o ID
                    if hasattr(value, 'id'):
                        setattr(self, f"{attr_name}_id", value.id)
                        del kwargs[attr_name]

    @classmethod
    def _validate_fields(cls, kwargs: Dict) -> None:
        """Valida se os campos fornecidos existem na classe.

        Padrão: Defensive Programming - validação rigorosa para garantir a integridade dos dados.
        """
        for field in kwargs:
            if not hasattr(cls, field):
                raise AttributeError(f"Campo '{field}' não existe no modelo {cls.__name__}")

    @classmethod
    def _generate_fields(cls) -> str:
        """Gera a definição SQL dos campos e relacionamentos.

        Padrão: Template Method - define uma sequência de passos para construir a query SQL.
        """
        fields = []
        cls._relationships.clear()  # Garante que a lista de relacionamentos esteja limpa

        for attr_name, field in cls.__dict__.items():
            if isinstance(field, Field):
                fields.append(f"{attr_name} {field.to_sql()}")
                cls._process_field_relationships(attr_name, field)
            elif isinstance(field, Relationship):
                # Adiciona sufixo _id para indicar chave estrangeira
                fields.append(f"{attr_name}_id {field.to_sql()}")
                cls._store_relationship_metadata(attr_name, field)

        return ", ".join(fields)

    @classmethod
    def _process_field_relationships(cls, attr_name: str, field: Field) -> None:
        """Processa metadados de campos que são relacionamentos.

        Padrão: Strategy Pattern - delega o processamento dos metadados conforme a configuração do campo.
        """
        if field.foreign_key:
            cls._relationships.append({
                "field_name": attr_name,
                "ref_table": field.foreign_key[0],
                "ref_field": field.foreign_key[1],
                "unique": field.unique
            })

    @classmethod
    def _store_relationship_metadata(cls, attr_name: str, relationship: Relationship) -> None:
        """Armazena metadados de relacionamentos."""
        cls._relationships.append({
            "field_name": f"{attr_name}_id",  # Adiciona o sufixo _id
            "ref_table": relationship.ref_table,
            "ref_field": getattr(relationship, 'ref_column', 'id'),
            "unique": isinstance(relationship, OneToOne)
        })



    def __str__(self) -> str:
        return self._repr()

    def __repr__(self) -> str:
        return self._repr()

    def _repr(self) -> str:
        """Representação única para __str__ e __repr__."""
        attrs = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{self.__class__.__name__}({attrs})"
    
    def to_dict(self):
        """
        Converte o objeto atual em um dicionário, pegando todos os atributos da instância,
        incluindo os atributos privados e quaisquer atributos adicionais.
        """
        return {key: value for key, value in self.__dict__.items()}


__all__ = ["Model"] + fields_all + relationships_all + connection_all
