import json

from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE

from src.db.models.model import Model

# run "./shellserver src.shell.tabletrees development.ini" in /home/gvv/Projects/bestida

EXCLUDE_PREFIXES = ("CreateOpId", "ModifiedOpId")

def get_models():
    return [
        cls for cls in Model._decl_class_registry.values()
        if hasattr(cls, "__tablename__") and not cls.__tablename__.startswith("transaction") and
           not cls.__tablename__.endswith("Version")
    ]


def build_adjacency(models):
    tree = {m.__tablename__: [] for m in models}

    for model in models:
        mapper = class_mapper(model)

        for rel in mapper.relationships:
            if rel.key.startswith(EXCLUDE_PREFIXES):
                continue

            if (rel.direction.name == "ONETOMANY" or
                rel.direction.name == "MANYTOONE"):
                parent = model.__tablename__
                child = rel.mapper.class_.__tablename__
                if not child.endswith("Version"):
                    if rel.info.get("hidden", None) is None:
                        depth = rel.info.get("depth", 1) if rel.info else 1
                        tree[parent].append((child, depth))

    return tree

"""
def find_roots(models):
    has_parent = set()

    for model in models:
        mapper = class_mapper(model)

        for rel in mapper.relationships:
            if rel.key.startswith(EXCLUDE_PREFIXES):
                continue

            if rel.direction.name == "MANYTOONE":
                has_parent.add(model.__tablename__)

    return [
        m.__tablename__
        for m in models
        if m.__tablename__ not in has_parent
    ]
"""

def find_roots(models):
    has_children = set()
    has_parent = set()

    for model in models:
        mapper = class_mapper(model)
        table = model.__tablename__

        for rel in mapper.relationships:
            if rel.key.startswith(EXCLUDE_PREFIXES):
                continue

            if rel.direction is ONETOMANY:
                has_children.add(table)

            elif rel.direction is MANYTOONE:
                has_parent.add(table)

    return [
        m.__tablename__
        for m in models
        if m.__tablename__ in has_children
        or m.__tablename__ not in has_parent
    ]

def build_nested(tree, node, remaining_depth, visited=None):
    if visited is None:
        visited = set()

    if node in visited:
        return {"name": node, "children": []}

    visited.add(node)

    result = {"name": node, "children": []}

    if remaining_depth <= 0:
        return result

    for child, depth in tree.get(node, []):
        result["children"].append(
            build_nested(
                tree,
                child,
                depth - 1,          # 👈 relationship controls depth
                visited.copy()
            )
        )

    return result


def run(app):
    models = get_models()
    tree = build_adjacency(models)
    for k, v in tree.items():
        print(k, v)
    roots = find_roots(models)
    print("roots:", roots)
    forest = [
        build_nested(tree, root, remaining_depth=1)  # default root = 1 level
        for root in roots
    ]

    print(json.dumps(forest, indent=2))
