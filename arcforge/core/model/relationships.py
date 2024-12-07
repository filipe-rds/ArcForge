from arcforge.core.model.relationship_base import *
from arcforge.core.model.relationshipStrategy import *

# class OneToMany(RelationshipBase):
#     """Relacionamento One to Many."""
#     def __init__(self, related_class, on_delete="CASCADE"):
#         # Chama o construtor da classe base RelationshipBase
#         super().__init__(related_class, on_delete)
#         # Atribui o nome da tabela referenciada à propriedade ref_table
#         self.ref_table = related_class._table_name
#         self.ref_field = f"{related_class._table_name}_id"
#     def to_sql(self):
#         # Relacionamento One to Many (a chave estrangeira estará na tabela "muitos")
#         return f"INTEGER REFERENCES {self.ref_table}(id) ON DELETE {self.on_delete}"

class ManyToOne(RelationshipBase):
    """Relacionamento Many to One."""

    def __init__(self, related_class, on_delete="CASCADE"):
        # Chama o construtor da classe base RelationshipBase
        super().__init__(related_class, on_delete)
        # Atribui o nome da tabela referenciada à propriedade ref_table
        self.ref_table = related_class._table_name
        self.ref_field = f"{related_class._table_name}"

    def to_sql(self):
        # Relacionamento Many to One (a chave estrangeira também estará na tabela "muitos")
        return f"INTEGER REFERENCES {self.ref_table}(id) ON DELETE {self.on_delete}"

class OneToOne(RelationshipBase):
    """Relacionamento One to One."""
    def __init__(self, related_class, on_delete="CASCADE"):
        # Chama o construtor da classe base RelationshipBase
        super().__init__(related_class, on_delete)
        # Atribui o nome da tabela referenciada à propriedade ref_table
        self.ref_table = related_class._table_name
        self.ref_field = f"{related_class._table_name}"

    def to_sql(self):
        # Relacionamento One to One (a chave estrangeira estará na tabela "um")
        return f"INTEGER REFERENCES {self.ref_table}(id) ON DELETE {self.on_delete}"
    
# class ManyToMany(RelationshipBase):
#     """Relacionamento Many to Many."""
#     def to_sql(self):
#         # Relacionamento Many to Many (a chave estrangeira estará na tabela de junção)
#         return f"INTEGER REFERENCES {self.related_class._table_name}(id) ON DELETE {self.on_delete}"