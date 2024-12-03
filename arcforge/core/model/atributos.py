class  Field:
    """Classe base para definir campos."""

    def __init__(self, field_type, primary_key=False, unique=False, nullable=True, default=None):
        self.field_type = field_type
        self.primary_key = primary_key
        self.unique = unique
        self.nullable = nullable
        self.default = default

    #Transformando os atributos da classe Field em uma string SQL
    def to_sql(self):
        sql_definition = self.field_type  # Começa com o tipo de dado
        
        # Adiciona a restrição PRIMARY KEY, se houver
        if self.primary_key:
            sql_definition += " PRIMARY KEY"
        
        # Adiciona UNIQUE, se houver
        if self.unique:
            sql_definition += " UNIQUE"
        
        # Adiciona NOT NULL, se o campo não for nullable
        if not self.nullable:
            sql_definition += " NOT NULL"
        
        # Adiciona o valor default, se houver
        if self.default is not None:
            sql_definition += f" DEFAULT {self.default}"
        
        return sql_definition
