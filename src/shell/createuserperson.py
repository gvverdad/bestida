from src.db import db_session, sqa

# run "./shellserver src.shell.createuserperson development.ini" in /home/gvv/Projects/bestida

def run(app):
    session = db_session()

    users = session.query(sqa.get_model("Users")).all()

    for user in users:
        if user.Personal is None:
            person = sqa.get_model("UserPersons")()
            person.Title_Id = 1
            person.Gender_Id = 1
            person.FirstName = "Firstname"
            person.LastName = "Lastname"
            session.add(person)

            user.Personal = person

    session.commit()

