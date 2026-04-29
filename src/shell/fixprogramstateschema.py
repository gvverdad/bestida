import ast
from src.db import db_session, sqa

# run "./shellserver src.shell.fixprogramstateschema development.ini" in /home/gvv/Projects/gvv


def run(app):
    session = db_session()

    prog_states = session.query(sqa.get_model("ProgramStates")).all()

    for ps in prog_states:
        state = ast.literal_eval(ps.State)
        print(state)
        break
        #state["grid_fields"] = state["grid_fields"][0]
        #ps.State = str(state)
        #session.add(ps)

    #session.commit()