class Field:
    """Classe base para definir campos."""
    def __init__(self, field_type, primary_key=False, unique=False, nullable=True, default=None,foreign_key=None):
        self.field_type = field_type
        self.primary_key = primary_key
        self.unique = unique
        self.nullable = nullable
        self.default = default
        self.foreign_key = foreign_key

    def to_sql(self):
        sql_fragment = f"{self.field_type}"
        if self.primary_key:
            sql_fragment += " PRIMARY KEY"
        if self.unique:
            sql_fragment += " UNIQUE"
        if not self.nullable:
            sql_fragment += " NOT NULL"
        if self.default is not None:
            sql_fragment += f" DEFAULT {self.default}"
        if self.foreign_key is not None:
            sql_fragment += f" REFERENCES {self.foreign_key}"
        return sql_fragment

    def __str__(self):
        # Pegando todos os atributos da instância (exceto métodos e atributos especiais)
        atributos = vars(self)
        # Criando uma string que mostra o nome do atributo e o valor
        atributos_str = ", ".join(f"{key}={value}" for key, value in atributos.items())
        return f"{self.__class__.__name__}({atributos_str})"