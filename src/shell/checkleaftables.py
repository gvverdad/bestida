from sqlalchemy.inspection import inspect
from sqlalchemy.orm.interfaces import MANYTOONE

def is_leaf_table(cls, Base):
    mapper = inspect(cls)

    # -------------------------
    # 1. Must NOT depend on others (no MANYTOONE)
    # -------------------------
    for rel in mapper.relationships:
        if rel.direction is MANYTOONE:
            return False

        # optional: exclude many-to-many tables
        if rel.secondary is not None:
            return False

    # -------------------------
    # 2. Must be referenced by others (incoming MANYTOONE)
    # -------------------------
    for other_cls in Base._decl_class_registry.values():
        if not hasattr(other_cls, "__table__"):
            continue

        other_mapper = inspect(other_cls)

        for rel in other_mapper.relationships:
            if rel.direction is MANYTOONE and rel.mapper.class_ == cls:
                return True

    return False

