# arcforge/core/models/relationships.py

def OneToOne(related_class, on_delete="CASCADE"):
    """Define um relacionamento One-to-One."""
    def decorator(cls):
        if not hasattr(cls, "_relationships"):
            cls._relationships = {}
        cls._relationships[related_class._table_name] = {
            "type": "OneToOne",
            "related_class": related_class,
            "on_delete": on_delete,
        }
        return cls
    return decorator


def OneToMany(related_class, on_delete="CASCADE"):
    """Define um relacionamento One-to-Many."""
    def decorator(cls):
        if not hasattr(cls, "_relationships"):
            cls._relationships = {}
        cls._relationships[related_class._table_name] = {
            "type": "OneToMany",
            "related_class": related_class,
            "on_delete": on_delete,
        }
        return cls
    return decorator


def ManyToOne(related_class, on_delete="CASCADE"):
    """Define um relacionamento Many-to-One."""
    def decorator(cls):
        if not hasattr(cls, "_relationships"):
            cls._relationships = {}
        cls._relationships[related_class._table_name] = {
            "type": "ManyToOne",
            "related_class": related_class,
            "on_delete": on_delete,
        }
        return cls
    return decorator


def ManyToMany(related_class):
    """Define um relacionamento Many-to-Many."""
    def decorator(cls):
        if not hasattr(cls, "_relationships"):
            cls._relationships = {}
        cls._relationships[related_class._table_name] = {
            "type": "ManyToMany",
            "related_class": related_class,
        }
        return cls
    return decorator
