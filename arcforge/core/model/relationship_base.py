class RelationshipBase:
    """Classe base para relacionamentos."""

    def __init__(self, related_class, on_delete="CASCADE"):
        self.related_class = related_class
        self.on_delete = on_delete

    def to_sql(self):
        """Método abstrato para retornar a SQL do relacionamento"""
        pass

    def __str__(self):
        # Pegando todos os atributos da instância (exceto métodos e atributos especiais)
        atributos = vars(self)
        # Criando uma string que mostra o nome do atributo e o valor
        atributos_str = ", ".join(f"{key}={value}" for key, value in atributos.items())
        return f"{self.__class__.__name__}({atributos_str})"
