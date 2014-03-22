from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import relationship, sessionmaker


engine = None
Base = declarative_base()


class File(Base):
    __tablename__ = 'File'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    file_type = Column(String)
    parent = relationship('File')

    def __repr__(self):
        return "<File: /n name=’%s’,/n type=’%s’ >" % (
            self.name, self.file_type)


def __create_database__():
    engine = create_engine('’sqlite:///database/')
    return engine


def get_engine():
    return engine if engine else __create_database__()


def insert_data(engine, file_name, file_type, paren):
    Session = sessionmaker(bind=engine)
    session = Session()
    parent = session.query(File).filter(File.name == paren)
    tmp = File(name=file_name, file_type=file_type, parent=parent)
    session.add(tmp)
    session.commit()
