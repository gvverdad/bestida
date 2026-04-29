import json

from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE, MANYTOMANY

from src.db.models.model import Model

# run "./shellserver src.shell.dbgraph development.ini" in /home/gvv/Projects/bestida

EXCLUDE_PREFIXES = ("CreateOpId", "ModifiedOpId")
ROOT_TABLES = ["Users", "Companies", "Products", "Warehouses"]


# ----------------------------
# Load models
# ----------------------------
def get_models():
    return {
        cls.__tablename__: cls
        for cls in Model._decl_class_registry.values()
        if hasattr(cls, "__tablename__") and not cls.__tablename__.startswith("transaction") and
           not cls.__tablename__.endswith("Version")
    }


# ----------------------------
# Build graph (WITH ORDER)
# ----------------------------
def build_graph(models):
    graph = {name: [] for name in models}

    for name, model in models.items():
        mapper = class_mapper(model)

        # preserves declaration order
        for i, (rel_name, rel) in enumerate(mapper.relationships.items()):

            if rel.key.startswith(EXCLUDE_PREFIXES):
                continue

            target = rel.mapper.class_.__tablename__
            if not target.endswith("Version"):
                if rel.info.get("hidden", None) is None:

                    if rel.direction is ONETOMANY:
                        rel_type = "ONETOMANY"
                    elif rel.direction is MANYTOONE:
                        rel_type = "MANYTOONE"
                    elif rel.direction is MANYTOMANY:
                        rel_type = "MANYTOMANY"
                    else:
                        rel_type = "OTHER"

                    # determine cardinality
                    if rel.direction is ONETOMANY:
                        if rel.uselist:
                            cardinality = "1:n"
                        else:
                            cardinality = "1:1"
                    elif rel.direction is MANYTOONE:
                        cardinality = "n:1"
                    elif rel.direction is MANYTOMANY:
                        cardinality = "n:n"
                    else:
                        cardinality = "?"

                    graph[name].append({
                        "to": target,
                        "type": rel_type,
                        "field": rel.key,
                        "depth": rel.info.get("depth") if rel.info else None,
                        "order": i,
                        "cardinality": cardinality
                    })

    return graph


# ----------------------------
# Build tree
# ----------------------------
def build_tree(graph, node, level=1, remaining_depth=2, path=None):
    if path is None:
        path = []

    # 🚫 prevent cycles (path-based)
    if node in path:
        return {"name": node, "level": level, "children": []}

    path = path + [node]

    result = {
        "name": node,
        "level": level,
        "children": []
    }

    # ✅ SORT by definition order
    edges = sorted(graph.get(node, []), key=lambda x: x["order"])

    for edge in edges:
        child_name = edge["to"]

        child_node = {
            "name": child_name,
            "field": edge["field"],
            "type": edge["type"],
            "level": level + 1,
            "children": []
        }

        # 🎯 ONLY recurse ONETOMANY
        if edge["type"] == "ONETOMANY":

            # depth logic
            if edge["depth"] is not None:
                next_depth = edge["depth"]
            else:
                next_depth = remaining_depth - 1

            if next_depth > 0:
                subtree = build_tree(
                    graph,
                    child_name,
                    level + 1,
                    next_depth,
                    path
                )
                child_node["children"] = subtree["children"]

        # MANYTOONE → included but not expanded

        result["children"].append(child_node)

    return result

def tree_to_graph(tree, graph):
    nodes = []
    edges = []

    def walk(node, parent=None, parent_table=None):
        node_id = id(node)
        table_name = node["name"]

        nodes.append({
            "id": node_id,
            "label": f"{table_name}\n(L{node['level']})",
            "table": table_name,
            "relationships": graph.get(table_name, [])
        })

        if parent and parent_table:
            # find matching edge
            edge_info = next(
                (e for e in graph[parent_table]
                 if e["to"] == table_name and e["field"] == node.get("field")),
                None
            )

            label = node.get("field", "")
            if edge_info:
                label += f" ({edge_info['cardinality']})"

            edges.append({
                "from": parent,
                "to": node_id,
                "label": label
            })

        for child in node.get("children", []):
            walk(child, node_id, table_name)

    for root in tree:
        walk(root)

    return nodes, edges


def generate_html(tree, graph, filename="graph.html"):

    nodes, edges = tree_to_graph(tree, graph)

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <title>ORM Graph</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    body {{ margin: 0; font-family: Arial; }}
    #network {{
      width: 100%;
      height: 100vh;
      border: 1px solid #ccc;
    }}
  </style>
</head>
<body>

<div id="network"></div>

<script>
  const nodes = new vis.DataSet({json.dumps(nodes)});
  const edges = new vis.DataSet({json.dumps(edges)});

  const container = document.getElementById('network');
  const data = {{ nodes, edges }};

  const options = {{
    layout: {{
      hierarchical: {{
        direction: "UD",
        sortMethod: "directed"
      }}
    }},
    physics: false,
    nodes: {{
      shape: "box",
      font: {{ size: 14 }}
    }},
    edges: {{
      arrows: "to",
      font: {{ align: "middle" }}
    }}
  }};

  new vis.Network(container, data, options);
</script>

</body>
</html>
"""

    with open(filename, "w") as f:
        f.write(html)
# ----------------------------
# MAIN
# ----------------------------
def run(app):
    models = get_models()
    graph = build_graph(models)

    forest = [
        build_tree(graph, root, level=1, remaining_depth=2)
        for root in ROOT_TABLES
        if root in graph
    ]

    #print(json.dumps(forest, indent=2))

    generate_html(forest, graph)
    print("graph.html generated")