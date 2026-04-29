from src.db import db_session, sqa

# run "./shellserver src.shell.changepassword development.ini" in /home/gvv/Projects/gvv


def run(app):
    session = db_session()

    user = session.query(sqa.get_model("Users")).get(1)
    user.Password = "root"

    session.add(user)
    session.commit()
