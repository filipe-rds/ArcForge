import psycopg
from psycopg import sql
from arcforge.core.db.config import *
from arcforge.core.model.field import *
from arcforge.core.model.relationships import *


class Model:
    """Classe base para modelos."""
    _table_name = None
    _fields = {}
    _relationships = []
    
    def __init__(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)

    def __str__(self):
        # Pegando todos os atributos da instância (exceto métodos e atributos especiais)
        atributos = vars(self)
        # Criando uma string que mostra o nome do atributo e o valor
        atributos_str = ", ".join(f"{key}={value}" for key, value in atributos.items())
        return f"{self.__class__.__name__}({atributos_str})"
    
    def __repr__(self):
        # Pegando todos os atributos da instância (exceto métodos e atributos especiais)
        atributos = vars(self)
        # Criando uma string que mostra o nome do atributo e o valor
        atributos_str = ", ".join(f"{key}={value}" for key, value in atributos.items())
        return f"{self.__class__.__name__}({atributos_str})"


    # Método para gerar os campos da tabela
    @classmethod
    def _generate_fields(cls):
        fields = []
        unique_constraints = []

        # Para cada atributo da classe (campos e relacionamentos)
        for attr, field in cls.__dict__.items():
            # Verifica se é um campo
            if isinstance(field, Field):
                fields.append(f"{attr} {field.to_sql()}")
            
            # Verifica se é um relacionamento
            elif isinstance(field, Relationship):
                # Chama o to_sql para gerar o relacionamento
                if isinstance(field, OneToOne):
                    # Adiciona a restrição UNIQUE explicitamente
                    unique_constraints.append(f"UNIQUE ({attr})")
                # fields.append(f"{attr} {field.to_sql()}")
                fields.append(f"{attr} {field.to_sql()}")
                # Armazena o relacionamento em _relationships
                cls._relationships.append({
                    "field_name": attr,
                    "ref_table": field.ref_table,
                    "ref_field": getattr(field, 'ref_field', None),
                    "unique": getattr(field, 'unique', False)
                })

        print(fields)
        fields_sql = ", ".join(fields + unique_constraints)
        return fields_sql

    



