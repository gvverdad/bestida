from src.db import db_session, sqa

# run "./shellserver src.shell.programname development.ini" in /home/bestida/Projects/gvv


def run(app):
    session = db_session()

    progs = session.query(sqa.get_model("Programs")).all()
    for prog in progs:
        if prog.Type == "Script":
            continue

        prog.Program = prog.URL.split("/")[-1]
        #prog.ProgramId = prog.ProgramId.replace(prog.Type, "", 1)

    session.commit()
