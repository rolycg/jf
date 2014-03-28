from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, backref
import time


engine = None
Base = declarative_base()


class File(Base):
    __tablename__ = 'File'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    root = Column(String)
    file_type = Column(String)
    parent_id = Column(Integer, ForeignKey('File._id'))
    parent = relationship('File', backref=backref('child_folder', remote_side=[_id]))

    def __init__(self, name, file_type, parent, root=None):
        self.name = name
        self.parent_id = parent
        self.file_type = file_type
        self.root = root

    def __repr__(self):
        return "<File: \n Name=’%s’,\n Type=’%s’ \n Parent: '%s'>" % (
            self.name, self.file_type, self.parent_id)


def create_database():
    engine = create_engine('sqlite:///database.db')
    Base.metadata.create_all(engine)
    return engine


def connect_database():
    engine = create_engine('sqlite:///database.db')
    return  engine


def get_database_all_elements(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    var = session.query(File).all()
    session.close()
    return var


def get_engine():
    return engine if engine else connect_database()


def insert_data(engine, file_name, file_type, paren, first=False):
    Session = sessionmaker(bind=engine)
    session = Session()
    if not first:
        parent = None
        for x in session.query(File).filter_by(name=paren):
            parent = x
        tmp = File(name=file_name, file_type=file_type, parent=parent._id)
    else:
        tmp = File(name=file_name, file_type=file_type, parent=-1, root=paren)
    session.add(tmp)
    session.commit()
    session.close()


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def do_commit(session):
    time1 = time.time()
    session.commit()
    return time.time() - time1


def dynamic_insert_data(session, path, dirs, files, f, session_count, total_files, count):
    for x in dirs:
        parent = session.query(File).filter_by(name=path).first()
        if not parent:
            a = do_commit(session)
            f.write('Elements: ' + str(session_count) + ' time: ' + str(a) + ' prop: ' + str(a / session_count) +
                    ' prop2: ' +
                    str(session_count / a) + '\n')
            session_count = 0
            parent = session.query(File).filter_by(name=path).first()
        tmp = File(name=x, file_type='Folder', parent=parent._id)
        session.add(tmp)
        total_files += 1
        session_count += 1
        if session_count == count:
            a = do_commit(session)
            f.write('Elements: ' + str(count) + ' time: ' + str(a) + ' prop: ' + str(a / count) + ' prop2: ' +
                    str(count / a) + '\n')
            count += 1
            session_count = 0
    for x in files:
        _type = x.split('.')
        parent = session.query(File).filter_by(name=path).first()
        if not parent:
            a = do_commit(session)
            f.write('Elements: ' + str(session_count) + ' time: ' + str(a) + ' prop: ' + str(a / session_count) +
                    ' prop2: ' +
                    str(session_count / a) + '\n')
            session_count = 0
            parent = session.query(File).filter_by(name=path).first()
        tmp = File(name=x, file_type='File: ' + _type[len(_type) - 1], parent=parent._id)
        total_files += 1
        session.add(tmp)
        session_count += 1
        if session_count == count:
            a = do_commit(session)
            f.write('Elements: ' + str(count) + ' time: ' + str(a) + ' prop: ' + str(a / count) + ' prop2: ' +
                    str(count / a) + '\n')
            count += 1
            session_count = 0
    return session, session_count, total_files, count


def get_address(engine, item):
    address = ''
    Session = sessionmaker(bind=engine)
    session = Session()
    while 1:
        address = str(item.name) + '/' + address
        if item.parent_id == -1:
            break
        item = session.query(File).filter_by(_id=item.parent_id).first()
    if item.root:
        address = str(item.root) + '/' + address
    return address[:len(address) - 1]


def find_data(engine, words_list):
    Session = sessionmaker(bind=engine)
    session = Session()
    final_collection = []
    for item in session.query(File).filter(File.name.like('%' + words_list[0] + '%')):
        final_collection.append((item.name, item.file_type, get_address(engine, item)))
    return final_collection
