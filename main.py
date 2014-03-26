import os
from queue import Queue
from threading import Thread
import data_layer
from time import sleep

finished = True
paint = False


def dfs(path, q):
    global finished
    for path, dirs, files in os.walk(path):
        q.put((path, dirs, files))
    finished = False


def save_to_disk(engine, q, path):
    import time
    total = time.time()
    global paint
    global finished
    path2 = path.split('/')
    path2 = path2[len(path2) - 1]
    data_layer.insert_data(engine, path2, 'Folder', path, True)
    f = open('time_test.txt', 'w')
    session = data_layer.get_session(engine)
    l = []
    count = 1
    total_files = 1
    session_count = 0
    while not q.empty() and finished:
        path, dirs, files = q.get()
        path = path.split('/')
        path = path[len(path) - 1]
        for x in dirs:
            parent = session.query(data_layer.File).filter_by(name=path).first()
            if not parent:
                a = data_layer.dynamic_insert_data(engine, l, session=None)
                f.write('Elements: ' + str(session_count) + ' time: ' + str(a) + ' prop: ' + str(a / session_count) +
                        ' prop2: ' +
                        str(session_count / a) + '\n')
                session_count = 0
                l = []
                parent = session.query(data_layer.File).filter_by(name=path).first()
            tmp = data_layer.File(name=x, file_type='Folder', parent=parent._id)
            l.append(tmp)
            #session.add(tmp)
            total_files += 1
            session_count += 1
            if session_count == count:
                a = data_layer.dynamic_insert_data(engine, l, session=None)
                f.write('Elements: ' + str(count) + ' time: ' + str(a) + ' prop: ' + str(a / count) + ' prop2: ' +
                        str(count / a) + '\n')
                count += 1
                session_count = 0
                l = []
        for x in files:
            _type = x.split('.')
            parent = session.query(data_layer.File).filter_by(name=path).first()
            if not parent:
                a = data_layer.dynamic_insert_data(engine, l, session=None)
                f.write('Elements: ' + str(session_count) + ' time: ' + str(a) + ' prop: ' + str(a / session_count) +
                        ' prop2: ' +
                        str(session_count / a) + '\n')
                session_count = 0
                l = []
                parent = session.query(data_layer.File).filter_by(name=path).first()
            tmp = data_layer.File(name=x, file_type='File: ' + _type[len(_type) - 1], parent=parent._id)
            l.append(tmp)
            total_files += 1
            #session.add(tmp)
            session_count += 1
            if session_count == count:
                a = data_layer.dynamic_insert_data(engine, l, session=None)
                f.write('Elements: ' + str(count) + ' time: ' + str(a) + ' prop: ' + str(a / count) + ' prop2: ' +
                        str(count / a) + '\n')
                count += 1
                session_count = 0
                l = []
    if session_count > 0:
        a = data_layer.dynamic_insert_data(engine, l, session=None)
        f.write('Elements: ' + str(session_count) + ' time: ' + str(a) + '\n')
    paint = False
    f.write('Total time: ' + str(time.time() - total) + ' Total elements: ' + str(total_files))


def printing():
    global paint
    count = 0
    paint = True
    while paint:
        if count % 3 == 0:
            print('Indexing.', end='\r')
            count += 1
            sleep(0.5)
        elif count % 3 == 1:
            print('Indexing..', end='\r')
            count += 1
            sleep(0.5)
        if count % 3 == 2:
            print('Indexing...', end='\r')
            count += 1
            sleep(0.5)
    print('', end='\r')


if __name__ == '__main__':
    print('********** My Everything 2.0 **********')
    path = '/media/roly/Extra/Info'
    engine = ''
    if not os.path.exists('./database.db'):
        engine = data_layer.create_database()
        _queue = Queue()
        t = Thread(target=dfs, args=(path, _queue))
        t.start()
        t2 = Thread(target=save_to_disk, args=(engine, _queue, path))
        t2.start()
        t3 = Thread(target=printing)
        t3.start()
        while paint:
            sleep(0.8)
    engine = data_layer.get_engine()
    while 1:
        print('Enter keywords:')
        words = input()
        for x, y, z in data_layer.find_data(engine, words.split(' ')):
            print('>Name: ' + str(x) + '\n' + '>File Type: ' + str(y) + '\n' + '>Address: ' + str(z) + '\n')
        print('Press any key for continue or write exit to finish')
        end = input()
        if end.lower() == 'exit':
            break
