from src.db import db_session, sqa

# run "./shellserver src.shell.personintegrity development.ini" in /home/gvv/Projects/bestida

def run(app):
    session = db_session()

    user_persons = session.query(sqa.get_model("UserPersons")).all()

    for person in user_persons:
        user = session.query(sqa.get_model("UserPersons")).get(person.ItemUser_Id)
        if user is None:
            for address in person.Addresses:
                session.delete(address)
            for phones in person.Phones:
                session.delete(phones)
            for email in person.Emails:
                session.delete(email)
            session.delete(person)

    session.commit()


