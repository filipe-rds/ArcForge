from abc import ABC, abstractmethod

class Relationship(ABC):
    """Classe base abstrata para relacionamentos."""

    def __init__(self, related_class, on_delete="CASCADE"):
        # Atribui o nome da tabela referenciada à propriedade ref_table
        self.ref_table = related_class._table_name
        self.ref_field = f"{related_class._table_name}"
        self.on_delete = on_delete

    def __str__(self):
        # Pegando todos os atributos da instância (exceto métodos e atributos especiais)
        atributos = vars(self)
        # Criando uma string que mostra o nome do atributo e o valor
        atributos_str = ", ".join(f"{key}={value}" for key, value in atributos.items())
        return f"{self.__class__.__name__}({atributos_str})"

    @abstractmethod
    def to_sql(self):
        """Método abstrato para retornar a SQL do relacionamento"""
        pass


class ManyToOne(Relationship):
    """Relacionamento Many to One."""

    def to_sql(self):
        # Relacionamento Many to One (a chave estrangeira também estará na tabela "muitos")
        return f"INTEGER REFERENCES {self.ref_table}(id) ON DELETE {self.on_delete}"

class OneToOne(Relationship):
    """Relacionamento One to One."""

    def to_sql(self):
        # Relacionamento One to One (a chave estrangeira estará na tabela "um")
        return f"INTEGER REFERENCES {self.ref_table}(id) ON DELETE {self.on_delete}"
    
# class ManyToMany(RelationshipBase):
#     """Relacionamento Many to Many."""

#     def to_sql(self):
#         # Relacionamento Many to Many (a chave estrangeira estará na tabela de junção)
#         return f"INTEGER REFERENCES {self.related_class._table_name}(id) ON DELETE {self.on_delete}"