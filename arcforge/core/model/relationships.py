from abc import ABC, abstractmethod
from enum import Enum
from typing import Type, Union
from arcforge.core.db.connection import DatabaseConnection  # Ajuste o caminho conforme sua estrutura

# -----------------------------------------------------------------------------
# Padrão de Projeto: Enum
# A classe OnDeleteAction utiliza o padrão Enum para padronizar as ações disponíveis
# na cláusula ON DELETE.
# -----------------------------------------------------------------------------
class OnDeleteAction(str, Enum):
    CASCADE = "CASCADE"
    RESTRICT = "RESTRICT"
    SET_NULL = "SET NULL"
    NO_ACTION = "NO ACTION"
    SET_DEFAULT = "SET DEFAULT"

# -----------------------------------------------------------------------------
# Padrão de Projeto: Template Method
# A classe Relationship define uma interface para a geração de SQL de relacionamentos,
# permitindo que as subclasses especializem o método to_sql.
# -----------------------------------------------------------------------------
class Relationship(ABC):
    def __init__(
            self,
            related_class: Type,
            on_delete: Union[OnDeleteAction, str] = OnDeleteAction.CASCADE,
            ref_column: str = "id"
    ):
        # Validação da classe relacionada
        if not hasattr(related_class, '_table_name'):
            raise AttributeError("A classe relacionada deve possuir '_table_name'")
        # Conversão de string para enum, se necessário
        if isinstance(on_delete, str):
            on_delete = OnDeleteAction(on_delete.upper())

        self.ref_table = related_class._table_name
        self.ref_column = ref_column
        self.on_delete = on_delete

    @abstractmethod
    def to_sql(self) -> str:
        """Retorna a definição SQL do relacionamento."""
        pass

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"ref_table={self.ref_table}, "
            f"ref_column={self.ref_column}, "
            f"on_delete={self.on_delete.value})"
        )

# -----------------------------------------------------------------------------
# Implementação com Descritor para relacionamento Many-to-One (Lazy Loading)
# -----------------------------------------------------------------------------
class ManyToOne(Relationship):
    def __init__(self, related_class: Type,
                 on_delete: Union[OnDeleteAction, str] = OnDeleteAction.CASCADE,
                 ref_column: str = "id"):
        super().__init__(related_class, on_delete, ref_column)
        self.related_class = related_class

    def __set_name__(self, owner, name):
        # Armazena o nome do atributo no modelo (por exemplo, "cliente")
        self.attr_name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self  # Acesso via classe retorna o próprio descritor

        # Se já carregamos o objeto relacionado, retorne-o
        if self.attr_name in instance.__dict__:
            value = instance.__dict__[self.attr_name]
            if not isinstance(value, ManyToOne):
                return value

        # Busca o valor da chave estrangeira armazenado como "<nome_atributo>_id"
        fk_value = instance.__dict__.get(f"{self.attr_name}_id")
        if fk_value is None:
            return None

        # Obtém a instância única de DatabaseConnection e utiliza o método read para buscar o objeto
        db = DatabaseConnection()
        related_obj = db.read(self.related_class, fk_value)
        # Armazena o objeto carregado para evitar nova consulta
        instance.__dict__[self.attr_name] = related_obj
        return related_obj

    def __set__(self, instance, value):
        # Permite atribuir diretamente o objeto relacionado e atualiza também a foreign key
        if value is not None and not isinstance(value, self.related_class):
            raise ValueError(
                f"Espera-se uma instância de {self.related_class.__name__} para o relacionamento '{self.attr_name}'"
            )
        instance.__dict__[self.attr_name] = value
        instance.__dict__[f"{self.attr_name}_id"] = value.id if value is not None else None

    def to_sql(self) -> str:
        return (
            f"INTEGER REFERENCES {self.ref_table}({self.ref_column}) "
            f"ON DELETE {self.on_delete.value}"
        )

# -----------------------------------------------------------------------------
# Implementação para relacionamento One-to-One (baseada em ManyToOne)
# -----------------------------------------------------------------------------
class OneToOne(ManyToOne):
    def to_sql(self) -> str:
        return (
            f"INTEGER REFERENCES {self.ref_table}({self.ref_column}) "
            f"ON DELETE {self.on_delete.value} UNIQUE"
        )

# -----------------------------------------------------------------------------
# Implementação para relacionamento Many-to-Many (placeholder)
# -----------------------------------------------------------------------------
class ManyToMany(Relationship):
    def __init__(self, through: Type, **kwargs):
        """
        Args:
            through: Classe da tabela de junção.
        """
        super().__init__(**kwargs)
        if not hasattr(through, '_table_name'):
            raise AttributeError("A tabela de junção deve possuir '_table_name'")
        self.through_table = through._table_name

    def __set_name__(self, owner, name):
        self.attr_name = name

    def __get__(self, instance, owner):
        # O carregamento dinâmico de Many-to-Many geralmente requer uma consulta à tabela de junção.
        # Essa implementação deverá ser personalizada conforme os requisitos do projeto.
        raise NotImplementedError("ManyToMany requer tratamento especial para carregamento dinâmico.")

    def to_sql(self) -> str:
        raise NotImplementedError("ManyToMany requer tratamento especial na migração.")


__all__ = ["OnDeleteAction", "Relationship", "ManyToOne", "OneToOne", "ManyToMany"]