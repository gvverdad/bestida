from src.db import db_session, sqa

# run "./shellserver src.shell.deleteprogramstates development.ini" in /home/gvv/Projects/bestida

def run(app):
    session = db_session()

    records = session.query(sqa.get_model("ProgramStates")).all()
    for record in records:
        session.delete(record)

    session.commit()
