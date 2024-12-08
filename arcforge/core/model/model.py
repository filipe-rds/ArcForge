import psycopg2
from psycopg2 import sql
from arcforge.core.db.config import *
from arcforge.core.model.field import *
from arcforge.core.model.relationshipStrategy import *
from arcforge.core.model.relationships import *

# class ForeignKey:
#     """Representa uma chave estrangeira."""

#     def __init__(self, related_class, on_delete="CASCADE"):
#         self.related_class = related_class
#         self.on_delete = on_delete

#     def to_sql(self, related_table_name):
#         return f"INTEGER REFERENCES {related_table_name}(id) ON DELETE {self.on_delete}"


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


    # @classmethod
    # def add_relationship(cls, field_name, ref_table, ref_field):
    #     cls._relationships.append({
    #         'field_name': field_name,
    #         'ref_table': ref_table,
    #         'ref_field': ref_field
    #     })


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
            elif isinstance(field, RelationshipBase):
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

    



    # @classmethod
    # def _create_relationships(cls):
    #     """Cria tabelas para relacionamentos Many-to-Many."""
    #     for related_table, config in cls._relationships.items():
    #         if config["type"] == "ManyToMany":
    #             join_table = f"{cls._table_name}_{related_table}"
    #             try:
    #                 create_table_query = sql.SQL("""
    #                     CREATE TABLE IF NOT EXISTS {join_table} (
    #                         {left_table}_id INTEGER REFERENCES {left_table}(id),
    #                         {right_table}_id INTEGER REFERENCES {right_table}(id),
    #                         PRIMARY KEY ({left_table}_id, {right_table}_id)
    #                     );
    #                 """).format(
    #                     join_table=sql.Identifier(join_table),
    #                     left_table=sql.Identifier(cls._table_name),
    #                     right_table=sql.Identifier(related_table),
    #                 )
    #                 with cls._conexao.cursor() as cursor:
    #                     cursor.execute(create_table_query)
    #                     cls._conexao.commit()
    #             except psycopg2.Error as e:
    #                 raise RuntimeError(
    #                     f"Erro ao criar relacionamento Many-to-Many com '{related_table}'.") from e

    # Método para salvar os dados


    # @classmethod
    # def add_relationship(cls, related_class, rel_type):
    #     """Adiciona configuração de relacionamento."""
    #     cls._relationships[related_class._table_name] = {
    #         "related_class": related_class, "type": rel_type}

    # @classmethod
    # def filter(cls, **conditions):
    #     """Filtra os registros com base nas condições fornecidas."""
    #     cls.set_conexao()
    #     where_clauses = []
    #     values = []

    #     for field, value in conditions.items():
    #         if hasattr(cls, field):
    #             where_clauses.append(f"{field} = %s")
    #             values.append(value)

    #     if not where_clauses:
    #         raise ValueError("Nenhuma condição foi fornecida para o filtro.")

    #     where_clause = " AND ".join(where_clauses)

    #     query = sql.SQL("""
    #         SELECT * FROM {table}
    #         WHERE {where_clause}
    #     """).format(
    #         table=sql.Identifier(cls._table_name),
    #         where_clause=sql.SQL(where_clause)
    #     )

    #     try:
    #         with cls._conexao.cursor() as cursor:
    #             cursor.execute(query, values)
    #             result = cursor.fetchall()
    #             return result  # Retorna os registros filtrados
    #     except psycopg2.Error as e:
    #         print(e)
    #         raise RuntimeError(f"Erro ao realizar o filtro na tabela '{cls._table_name}'.") from e


# Decorators para Relacionamentos

# def OneToOne(related_class, on_delete="CASCADE"):
#     """Define um relacionamento One-to-One."""
#     def decorator(cls):
#         cls._relationships[related_class._table_name] = {
#             "type": "OneToOne",
#             "related_class": related_class,
#             "on_delete": on_delete,
#         }
#         setattr(cls, f"{related_class._table_name}_id",
#                 ForeignKey(related_class, on_delete))
#         return cls
#     return decorator


# def ManyToOne(related_class, on_delete="CASCADE"):
#     """Define um relacionamento Many-to-One."""
#     def decorator(cls):
#         cls._relationships[related_class._table_name] = {
#             "type": "ManyToOne",
#             "related_class": related_class,
#             "on_delete": on_delete,
#         }
#         setattr(cls, f"{related_class._table_name}_id",
#                 ForeignKey(related_class, on_delete))
#         return cls
#     return decorator


# def OneToMany(related_class):
#     """Define um relacionamento One-to-Many."""
#     def decorator(cls):
#         cls._relationships[related_class._table_name] = {
#             "type": "OneToMany",
#             "related_class": related_class,
#         }
#         return cls
#     return decorator


# def ManyToMany(related_class):
#     """Define um relacionamento Many-to-Many."""
#     def decorator(cls):
#         cls.add_relationship(related_class, "ManyToMany")
#         return cls
#     return decorator
