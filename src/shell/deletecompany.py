from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE, MANYTOMANY

from src.db import db_session, sqa
from src.db.models.functions import get_app_tables_choices

# run "./shellserver src.shell.deletecompany development.ini" in /home/gvv/Projects/bestida

# these tables/fields are also defined in copycompany.py
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


def run(app):
    session = db_session()

    company = session.query(sqa.get_model("Companies")).get(2)

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
        if table_info.get("companyField") is None:
            continue

        mapper = class_mapper(sqa.get_model(name))
        if is_leaf(mapper):
            leaves.append(name)
        elif is_branch(mapper):
            branches.append(name)

    print("ROOT TABLES:")
    # reverse
    for root in reversed(ROOT_TABLES):
        table_info = sqa.get_table_info(root)
        filters = dict()
        filters[table_info["companyField"]] = company.Id
        records = session.query(sqa.get_model(root)).filter_by(**filters).all()
        for record in records:
            session.delete(record)
        if records:
            session.commit()
            print(root)

    print("\nBRANCH TABLES:")
    for branch in branches:
        table_info = sqa.get_table_info(branch)
        filters = dict()
        filters[table_info["companyField"]] = company.Id
        records = session.query(sqa.get_model(branch)).filter_by(**filters).all()
        for record in records:
            session.delete(record)
        if records:
            session.commit()
            print(branch)

    print("\nLEAF TABLES:")
    for leaf in leaves:
        table_info = sqa.get_table_info(leaf)
        filters = dict()
        filters[table_info["companyField"]] = company.Id
        records = session.query(sqa.get_model(leaf)).filter_by(**filters).all()
        for record in records:
            session.delete(record)
        if records:
            session.commit()
            print(leaf)
