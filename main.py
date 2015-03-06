import os
from queue import Queue
from threading import Thread
from time import sleep
import getpass
import hashlib

import comunication_layer as cl
import watch_layer
import data_layer as data_layer_py


finished = True
paint = False


def dfs(path, q):
    global finished
    for _path, dirs, files in os.walk(path):
        q.put((_path, dirs, files))
    finished = False


def save_to_disk(engine, q, path):
    global paint
    global finished
    list_file_tmp = {}
    path2 = path.split(os.sep)
    path2 = path2[len(path2) - 1]
    engine.insert_peer()
    peer = engine.get_uuid_from_peer()
    engine.insert_data(id=1, file_name=path2, file_type='Folder', parent=path, generation=0, first=True, peer=peer)
    count = 1
    total_files = 2
    session_count = 0
    list_file_tmp[path2] = 1
    while not q.empty() or finished:
        path, dirs, files = q.get()
        complete_path = path
        path = path.split(os.sep)
        path = path[len(path) - 1]
        session_count, total_files, count = data_layer.dynamic_insert_data(path, dirs, files,
                                                                           session_count,
                                                                           total_files, count,
                                                                           complete_path,
                                                                           peer=peer)
    paint = False
    data_layer.database.commit()
    # f.write('Total time: ' + str(time.time() - total) + ' Total elements: ' + str(total_files))


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
    path = '/media/roly/Extra/Series/'
    print('Username:')
    user_name = input()
    password = getpass.getpass()
    while len(password) > 32:
        print('Password must be smaller than 32 characters')
        password = getpass.getpass()
    jump = 1
    data_layer = None
    if not os.path.exists('./database.db'):
        jump = 0
        data_layer = data_layer_py.DataLayer('database.db')
        data_layer.create_databases()
        sha = hashlib.md5(password.encode())
        data_layer.insert_username_password(user_name, sha.hexdigest())
        _queue = Queue()
        t = Thread(target=dfs, args=(path, _queue))
        t.start()
        t2 = Thread(target=save_to_disk, args=(data_layer, _queue, path))
        t2.start()
        t3 = Thread(target=printing)
        t3.start()
        while paint:
            sleep(0.8)
    if not data_layer:
        data_layer = data_layer_py.DataLayer('database.db')
    while jump:
        u_p = data_layer.get_username_password()
        sha = hashlib.md5(password.encode())
        if user_name == u_p[0] and sha.hexdigest() == u_p[1]:
            break
        print('Username:')
        user_name = input()
        password = getpass.getpass()
    t4 = Thread(target=watch_layer.add_multi_platform_watch, args=(path,))
    t4.start()
    t5 = Thread(target=cl.start, args=())
    t5.start()
    data_layer_2 = data_layer_py.DataLayer('database.db')
    while 1:
        print('Enter keywords:')
        words = input()
        if not words.strip():
            continue
        with data_layer_py.semaphore:
            for item in data_layer.find_data(words.split()):
                print('>Name: ' + str(item[2]) + '\n' + '>File Type: ' + str(item[4]) + '\n' + '>Address: '
                      + str(data_layer_2.get_address(item[1], item[7])) + '\n' + '>Machine: ' +
                      data_layer_2.get_peer_from_uuid(item[7]) + '\n')
        print('Press any key for continue or write exit to finish')
        end = input()
        if end.lower() == 'exit':
            break
    t4._stop()
    t5._stop()
