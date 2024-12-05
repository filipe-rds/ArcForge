class RelationshipStrategy:
    """Interface para as estratégias de relacionamento."""

    def to_sql(self, related_class, on_delete):
        """Método abstrato para gerar a SQL do relacionamento"""
        raise NotImplementedError
