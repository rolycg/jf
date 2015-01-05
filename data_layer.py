import time
import socket
import uuid as uu

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy import Column, String, create_engine, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import relationship, sessionmaker, backref


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
    generation = Column(BigInteger)

    def __init__(self, name, file_type, parent, generation, root=None):
        self.name = name
        self.parent_id = parent
        self.file_type = file_type
        self.root = root
        self.generation = generation

    def __repr__(self):
        return "<File: \n Name=’%s’,\n Type=’%s’ \n Parent: '%s'>" % (
            self.name, self.file_type, self.parent_id)


class Login(Base):
    __tablename__ = 'Login'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Metadata(Base):
    __tablename__ = 'Metadata'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    _uuid = Column(String)
    pc_name = Column(String)
    ip_address = Column(String)
    last_generation = Column(BigInteger)

    def __init__(self, _uuid, pc_name, ip_address, generation=-1):
        self._uuid = _uuid
        self.pc_name = pc_name
        self.ip_address = ip_address
        self.last_generation = generation

    def __repr__(self):
        return "<Metadata: \n PC Name=’%s’,\n IP=’%s’>" % (
            self.pc_name, self.ip_address)


def create_database():
    engine = create_engine('sqlite:///database.db', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return engine


def connect_database():
    engine = create_engine('sqlite:///database.db', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    return engine


def get_database_all_elements(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    var = session.query(File).all()
    session.close()
    return var


def get_engine():
    return engine if engine else connect_database()


def get_max_generation():
    session = get_session(get_engine())
    l = [x[0] for x in session.query(File.generation).all()]
    if len(l):
        return max(l)
    else:
        return -1


def insert_username_password(username, password):
    engine = get_engine()
    session = get_session(engine)
    login = Login(username=username, password=password)
    session.add(login)
    session.commit()
    session.close()


def get_username_password():
    engine = get_engine()
    session = get_session(engine)
    var = session.query(Login).all()
    session.close()
    return var


def insert_peer(engine, uuid=None, pc_name=None, ip=None):
    session = get_session(engine)
    peer = None
    if not uuid and not pc_name and not ip:
        peer = Metadata(str(uu.uuid4()), socket.gethostname(), '127.0.0.1')
    else:
        peer = Metadata(uuid, pc_name, ip)
    session.add(peer)
    session.commit()
    session.close()


def edit_generation(engine, uuid, generation):
    session = get_session(engine)
    session.query(Metadata).filter(uuid).update({'last_generation': generation})
    session.commit()
    session.close()


def insert_data(engine, file_name, file_type, paren, generation, first=False):
    session = get_session(engine)
    if not first:
        parent = None
        for x in session.query(File).filter_by(name=paren):
            parent = x
        tmp = File(name=file_name, file_type=file_type, parent=parent._id, generation=generation)
    else:
        tmp = File(name=file_name, file_type=file_type, parent=-1, root=paren, generation=generation)
    session.add(tmp)
    session.commit()
    session.close()


def delete_data(engine, file_name):
    session = get_session(engine)
    session.query(File).filter_by(name=file_name).delete()
    session.commit()
    session.close()


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def do_commit(session):
    time1 = time.time()
    session.commit()
    return time.time() - time1


def dynamic_insert_data(session, path, dirs, files, f, session_count, total_files, count, list_file_tmp):
    parent = list_file_tmp[path]
    session.autoflush = False
    for x in dirs:
        tmp = File(name=x, file_type='Folder', parent=parent, generation=0)
        list_file_tmp[x] = total_files
        session.add(tmp)
        total_files += 1
        session_count = len(session.new)
        if session_count == count:
            a = do_commit(session)
            f.write('Elements: ' + str(session_count) + ' time: ' + str(a) + ' prop: ' + str(a / count) + ' prop2: '
                    + str(count / a) + '\n')
            count += 1
            session_count = 0
    for x in files:
        _type = x.split('.')
        tmp = File(name=x, file_type='File: ' + _type[len(_type) - 1], parent=parent, generation=0)
        total_files += 1
        session.add(tmp)
        session_count = len(session.new)
        if session_count == count:
            a = do_commit(session)
            f.write('Elements: ' + str(session_count) + ' time: ' + str(a) + ' prop: ' + str(a / count) + ' prop2: '
                    + str(count / a) + '\n')
            count += 1
            session_count = 0
    return session, session_count, total_files, count, list_file_tmp


def get_address(engine, item):
    address = ''
    Session = sessionmaker(bind=engine)
    session = Session()
    while 1:
        if item.parent_id == -1:
            break
        address = str(item.name) + '/' + address
        item = session.query(File).filter_by(_id=item.parent_id).first()
    if item.root:
        address = str(item.root) + '/' + address
    return address[:len(address) - 1]


def find_data(engine, words_list):
    Session = sessionmaker(bind=engine)
    session = Session()
    a = session.query(File).filter(File.name.like('%' + words_list[0] + '%'))
    return a


