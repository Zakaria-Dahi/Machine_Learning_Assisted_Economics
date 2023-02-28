from database import *
from sqlalchemy.orm import sessionmaker


def test_insert(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    l = Location(name='Málaga')
    session.add(l)
    session.commit()
    session.close()


def test_query(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Location).all()
    for row in result:
        print(f"ID: {row.id} - Name: {row.name}")
    session.commit()
    session.close()


if __name__ == '__main__':
    engine = createDB()
    test_insert(engine)
    test_query(engine)