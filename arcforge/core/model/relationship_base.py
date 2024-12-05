class RelationshipBase:
    """Classe base para relacionamentos."""

    def __init__(self, related_class, on_delete="CASCADE"):
        self.related_class = related_class
        self.on_delete = on_delete

    def to_sql(self):
        """Método abstrato para retornar a SQL do relacionamento"""
        pass

