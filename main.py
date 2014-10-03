import os
from queue import Queue
from threading import Thread
from time import sleep
import time

import data_layer
import watch_layer


finished = True
paint = False


def dfs(path, q):
    global finished
    for _path, dirs, files in os.walk(path):
        q.put((_path, dirs, files))
    finished = False


def save_to_disk(engine, q, path):
    total = time.time()
    global paint
    global finished
    list_file_tmp = {}
    path2 = path.split('/')
    path2 = path2[len(path2) - 1]
    data_layer.insert_data(engine, path2, 'Folder', path, generation=0, first=True)
    name_txt = path2 + '.txt'
    f = open(name_txt, 'w')
    session = data_layer.get_session(engine)
    count = 1
    total_files = 2
    session_count = 0
    list_file_tmp[path2] = 1
    while not q.empty() or finished:
        path, dirs, files = q.get()
        path = path.split('/')
        path = path[len(path) - 1]
        session, session_count, total_files, count, list_file_tmp = data_layer.dynamic_insert_data(session, path, dirs,
                                                                                                   files, f,
                                                                                                   session_count,
                                                                                                   total_files, count,
                                                                                                   list_file_tmp)
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
    path = '/media/roly/Extra/Series'
    print('Username:')
    user_name = input()
    print('Password:')
    password = input()
    jump = 1
    if not os.path.exists('./database.db'):
        jump = 0
        engine = data_layer.create_database()
        data_layer.insert_username_password(user_name, password)
        _queue = Queue()
        t = Thread(target=dfs, args=(path, _queue))
        t.start()
        t2 = Thread(target=save_to_disk, args=(engine, _queue, path))
        t2.start()
        t3 = Thread(target=printing)
        t3.start()
        while paint:
            sleep(0.8)
    while jump:
        u_p = data_layer.get_username_password()
        if user_name == u_p[0].user_name and password == u_p[0].password:
            break
        print('Username:')
        user_name = input()
        print('Password:')
        password = input()

#   data_layer.insert_peer(engine)
    engine = data_layer.get_engine()
    t4 = Thread(target=watch_layer.add_multi_platform_watch, args=(path,))
    t4.start()
    #t5 = Thread(target=cl.broadcast, args=())
    #t5.start()
    while 1:
        print('Enter keywords:')
        words = input()
        for item in data_layer.find_data(engine, words.split(' ')):
            print('>Name: ' + str(item.name) + '\n' + '>File Type: ' + str(item.file_type) + '\n' + '>Address: '
                  + str(data_layer.get_address(engine, item)) + '\n')
        print('Press any key for continue or write exit to finish')
        end = input()
        if end.lower() == 'exit':
            break
    t4._stop()
    #t5.stop()
