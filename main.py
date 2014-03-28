import os
from queue import Queue
from threading import Thread
import data_layer
import watch_layer
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
    f = open('time_test3.txt', 'w')
    session = data_layer.get_session(engine)
    count = 1
    total_files = 1
    session_count = 0
    while not q.empty() or finished:
        path, dirs, files = q.get()
        path = path.split('/')
        path = path[len(path) - 1]
        session, session_count, total_files, count = data_layer.dynamic_insert_data(session, path, dirs, files, f,
                                                                                    session_count, total_files, count)
    if session_count > 0:
        a = data_layer.do_commit(session)
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
    t4 = Thread(target=watch_layer.add_linux_watch, args=(path,))
    t4.start()
    while 1:
        print('Enter keywords:')
        words = input()
        for x, y, z in data_layer.find_data(engine, words.split(' ')):
            print('>Name: ' + str(x) + '\n' + '>File Type: ' + str(y) + '\n' + '>Address: ' + str(z) + '\n')
        print('Press any key for continue or write exit to finish')
        end = input()
        if end.lower() == 'exit':
            break
