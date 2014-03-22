from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker


engine = None
Base = declarative_base()


class Files(Base):
    __tablename__ = 'Files'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    file_type = Column(String)
    child_id = Column(Integer, ForeignKey('Files._id'))
    parent = relationship('Files')

    def __init__(self, name, file_type, parent=None):
        self.name = name
        self.file_type = file_type
        if parent:
            self.parent = parent

    def __repr__(self):
        return "<File: \n Name=’%s’,\n Type=’%s’ \n Parent='%s'>" % (
            self.name, self.file_type, self.child_id)


def __create_database__():
    engine = create_engine('sqlite:///database.db')
    Base.metadata.create_all(engine)
    return engine


def __connect_database__():
    engine = create_engine('sqlite:///database.db')
    return  engine


def get_database_all_elements(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    var = session.query(Files).all()
    session.close()
    return var


def get_engine():
    return engine if engine else __connect_database__()


def insert_data(engine, file_name, file_type, paren):
    Session = sessionmaker(bind=engine)
    session = Session()
    parent = None
    for x in session.query(Files.name).filter_by(name=paren):
        parent = x
    tmp = Files(name=file_name, file_type=file_type, parent=parent)
    session.add(tmp)
    session.commit()
