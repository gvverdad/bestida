from src.db import db_session, sqa
from src.db.models.functions import get_app_tables_choices

# run "./shellserver src.shell.checkcompany2 development.ini" in /home/gvv/Projects/bestida

def run(app):
    session = db_session()

    exclude_tables = ["Companies"]

    company = session.query(sqa.get_model("Companies")).get(2)

    tables = get_app_tables_choices()
    for k, _ in tables:
        if k in exclude_tables:
            continue

        meta = sqa.get_model(k)  # DeclarativeMeta ORM model
        table_info = sqa.get_table_info(k)
        if "companyField" not in table_info:
            continue

        where = f"{table_info['companyField']} = {company.Id}"
        #records = session.query(meta).filter(sqa.where(where)).scalar()
        #if records is None:
        #    continue
        #print(k, where)

        records = session.query(meta).filter(sqa.where(where)).all()
        if len(records) == 0:
            continue

        for record in records:
            print(k, where, record.Id)
        #    session.delete(record)
        #    session.commit()


