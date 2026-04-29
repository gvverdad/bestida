from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE, MANYTOMANY
from sqlalchemy.inspection import inspect

from src.db import db_session, sqa
from src.db.models.functions import get_app_tables_choices

# run "./shellserver src.shell.copycompany development.ini" in /home/gvv/Projects/bestida

EXCLUDE_FIELDS = ("CreateOpId", "ModifiedOpId", "InactiveOpId", "Company", "versions",
                  "CreateTimeStamp", "ModifiedTimeStamp", "InactiveTimeStamp")
EXCLUDE_TABLES = ["Companies", "Users", "Bookmarks", "Tasks", "Spoolers", "Rulesets", "ProgramStates"]
TRIGGER_TABLES = ["FGStocks", "SalesOrders", "SalesAllocations", "SalesPickings",
                  "SalesPackings", "SalesInvoices"]
ROOT_TABLES = ["Products", "Warehouses", "SalesAccounts", "Customers", "Suppliers",
               "Costs", "ContractPriceDiscounts", "PriceBands", "PriceLists"]
TRANSACTION_TABLES = ["SalesOrderHeaders", "SalesOrderPickTickets", "SalesOrderInvoices",
               "SalesOrderCreditNotes", "POHeaders", "FGStockMovements"]

def is_leaf(mapper):
    # no MANYTOONE/MANYTOMANY/ONETOMANY
    for rel in mapper.relationships:
        if rel.key.startswith(EXCLUDE_FIELDS):
            continue
        if rel.info.get("hidden", False):
            continue

        if rel.direction is MANYTOONE:
            return False
        if rel.direction is ONETOMANY:
            return False
        if rel.direction is MANYTOMANY:
            return False

    return True

def is_branch(mapper):
    # when not is_leaf - check if root table
    for rel in mapper.relationships:
        if rel.key.startswith(EXCLUDE_FIELDS):
            continue
        if rel.info.get("hidden", False):
            continue
        if rel.key in ROOT_TABLES:
            return False

        if rel.direction is MANYTOONE:
            # MANYTOONE side of ONETOMANY
            # WarehouseArea - ManyToOne side of Warehouse  ItemWarehouse
            # Warehouse - OneToMany Areas
            # WarehouseArea.ItemWarehouse backref is None
            if rel.backref is None and rel.back_populates is not None:
                return False

    return True


def get_unique_index_fields(table):
    for idx in table.indexes:
        if idx.unique:
            return [col for col in idx.columns]  # Column object

    return list()

def resolve_fk(record, col, mapper, session, to_company):
    # find relationship that owns this FK column
    rel = next(
        (r for r in mapper.relationships if col in r.local_columns),
        None
    )
    if not rel:
        return getattr(record, col.key)

    # only care about MANYTOONE
    if rel.direction is not MANYTOONE:
        return None  # handled elsewhere (1:n, n:n)
    # ignore MANYTOONE backref
    # WarehouseArea - ManyToOne side of Warehouse  ItemWarehouse
    # Warehouse - OneToMany Areas
    # WarehouseArea.ItemWarehouse backref is None
    if rel.backref is None and rel.back_populates is not None:
        return None

    parent = getattr(record, rel.key)
    if parent is None:
        return None

    parent_cls = parent.__class__
    parent_mapper = inspect(parent_cls)
    parent_table = parent_mapper.local_table
    company_field = parent_table.info.get("companyField", None)
    index_columns = get_unique_index_fields(parent_table)

    filters = {}
    for col in index_columns:
        if col.key == company_field:
            filters[col.key] = to_company
        elif col.foreign_keys:
            value = getattr(parent, col.key)
            if value is not None:
                fk_val = resolve_fk(parent, col, parent_mapper, session, to_company)
                filters[col.key] = fk_val
            else:
                filters[col.key] = None
        else:
            filters[col.key] = getattr(parent, col.key)

    existing = None
    if filters:
        existing = session.query(parent_cls).filter_by(**filters).first()
    if existing:
        return existing.Id

    _, new_parent = clone(session, parent, to_company)
    return new_parent.Id if new_parent else None

def clone(session, record, to_company):
    cls = record.__class__
    mapper = inspect(cls)
    table = mapper.local_table
    index_columns = get_unique_index_fields(table)
    company_field = table.info.get("companyField", None)

    # check if new record exists
    filters = {}
    for col in index_columns:
        if col.key == company_field:
            filters[col.key] = to_company
            continue
        if col.foreign_keys:
            value = getattr(record, col.key)
            if value is not None:
                fk_val = resolve_fk(record, col, mapper, session, to_company)
                filters[col.key] = fk_val
            else:
                filters[col.key] = None
        else:
            filters[col.key] = getattr(record, col.key)

    if filters:
        existing = session.query(cls).filter_by(**filters).first()
        if existing:
            return False, existing

    # clone columns
    new_record = cls()
    visited = list()
    # use mapper.columns instead of table.colums to handle inherited tables
    for col in mapper.columns:
        if col.primary_key:
            continue
        if company_field and col.key == company_field:
            setattr(new_record, col.key, to_company)
            continue
        if not col.info.get("modifiable", True):
            continue
        if col.key.startswith(EXCLUDE_FIELDS):
            continue
        if col.foreign_keys:
            rel = next(
                (r for r in mapper.relationships if col in r.local_columns),
                None
            )
            if rel is not None:
                if rel.key in visited:
                    continue
                visited.append(rel.key)

            value = getattr(record, col.key)
            if value is not None:
                fk_val = resolve_fk(record, col, mapper, session, to_company)
                setattr(new_record, col.key, fk_val)
            continue

        value = getattr(record, col.key)
        setattr(new_record, col.key, value)

    session.add(new_record)
    session.flush()  # get PK

    # clone relationships
    for rel in mapper.relationships:
        if rel.lazy == 'dynamic':
            continue
        if rel.key.startswith(EXCLUDE_FIELDS):
            continue
        if rel.info.get("hidden", False):
            continue
        if rel.key in visited:
            continue
        else:
            visited.append(rel.key)

        # ignore MANYTOONE backref
        # WarehouseArea - ManyToOne side of Warehouse  ItemWarehouse
        # Warehouse - OneToMany Areas
        # WarehouseArea.ItemWarehouse backref is None
        if rel.direction is MANYTOONE and rel.backref is None and rel.back_populates is not None:
            continue

        value = getattr(record, rel.key)
        if not value:
            continue
        if rel.uselist:
            children = list()
            for val in value:
                _, child = clone(session, val, to_company)
                if child:
                    children.append(child)
            if children:
                setattr(new_record, rel.key, children)
        else:
            _, new_child = clone(session, value, to_company)
            if new_child is not None:
                setattr(new_record, rel.key, new_child)

    return True, new_record


def run(app):
    session = db_session()

    from_company = session.query(sqa.get_model("Companies")).get(1)
    to_company = session.query(sqa.get_model("Companies")).get(2)

    leaves = list()
    branches = list()

    tables = get_app_tables_choices()
    for name, _ in tables:
        if name in EXCLUDE_TABLES:
            continue
        if name in TRANSACTION_TABLES:
            continue
        if name in TRIGGER_TABLES:
            continue
        if name in ROOT_TABLES:
            continue
        table_info = sqa.get_table_info(name)
        if table_info.get("companyField", None) is None:
            continue

        mapper = class_mapper(sqa.get_model(name))
        if is_leaf(mapper):
            leaves.append(name)
        elif is_branch(mapper):
            branches.append(name)
    """
    print("LEAF TABLES:")
    for leaf in leaves:
        print(leaf)
    
    print("\nBRANCH TABLES:")
    for branch in branches:
        print(branch)

    print("\nROOT TABLES:")
    for root in ROOT_TABLES:
        print(root)
    """
    print("LEAF TABLES:")
    for leaf in leaves:
        table_info = sqa.get_table_info(leaf)
        filters = dict()
        filters[table_info["companyField"]] = from_company.Id
        records = session.query(sqa.get_model(leaf)).filter_by(**filters).all()
        total = len(records)
        created = 0
        for record in records:
            copied, _ = clone(session, record, to_company.Id)
            if copied:
                created += 1
        if len(records) > 0:
            session.commit()
        print(leaf, total, created)

    print("\nBRANCH TABLES:")
    for branch in branches:
        table_info = sqa.get_table_info(branch)
        filters = dict()
        filters[table_info["companyField"]] = from_company.Id
        records = session.query(sqa.get_model(branch)).filter_by(**filters).all()
        total = len(records)
        created = 0
        for record in records:
            copied, _ = clone(session, record, to_company.Id)
            if copied:
                created += 1
        if len(records) > 0:
            session.commit()
        print(branch, total, created)

    print("\nROOT TABLES:")
    for root in ROOT_TABLES:
        table_info = sqa.get_table_info(root)
        filters = dict()
        filters[table_info["companyField"]] = from_company.Id
        records = session.query(sqa.get_model(root)).filter_by(**filters).all()
        total = len(records)
        created = 0
        for record in records:
            copied, _ = clone(session, record, to_company.Id)
            if copied:
                created += 1
        if len(records) > 0:
            session.commit()
        print(root, total, created)
    """
    name = "Products"
    table_info = sqa.get_table_info(name)
    filters = dict()
    filters[table_info["companyField"]] = from_company.Id
    records = session.query(sqa.get_model(name)).filter_by(**filters).all()
    total = len(records)
    created = 0
    for record in records:
        copied, _ = clone(session, record, to_company.Id)
        if copied:
            created += 1
    if len(records) > 0:
        session.commit()
    print(name, total, created)
    """