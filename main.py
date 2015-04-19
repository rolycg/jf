import os
from queue import Queue, Empty
from threading import Thread
from time import sleep, localtime
import getpass
import hashlib
import time

import extra_functions as ef
import comunication_layer as cl
import watch_layer
import data_layer as data_layer_py
import external_devices_layer as ed


finished = True
paint = False
start_time = None


def dfs(path, q):
    for _path, dirs, files in os.walk(path):
        q.put((_path, dirs, files))


def save_to_disk(engine, q, peer):
    global paint
    global finished
    global start_time
    start_time = time.time()
    count = 1
    total_files = 2
    session_count = 0
    generation = engine.get_max_generation() + 1
    if not generation:
        generation = 0
    while 1:
        try:
            path, dirs, files = q.get(timeout=1)
            complete_path = path
            path = path.split(os.sep)
            path = path[len(path) - 1]
            session_count, total_files, count = engine.dynamic_insert_data(path, dirs, files,
                                                                           session_count,
                                                                           total_files, count,
                                                                           complete_path,
                                                                           peer=peer, generation=generation)
            while data_layer_py.query:
                time.sleep(0.5)
            if count > 100000:
                engine.database.commit()
                count = 0
        except Empty:
            break
    paint = False
    while data_layer_py.query:
        time.sleep(0.5)
    engine.database.commit()
    # TODO: Remove this


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


def start(paths):
    t4 = Thread(target=watch_layer.add_multi_platform_watch, args=(paths, Queue()))
    t4.start()
    t5 = Thread(target=cl.start, args=())
    t5.start()
    t6 = Thread(target=ed.start_observer, args=())
    t6.start()


def create(path=None):
    # TODO: put path  in None
    data_layer = data_layer_py.DataLayer('database.db')
    path = '/home/roly/file_system'
    paths = []
    if not path:
        paths = ef.get_initials_paths()
    else:
        paths = [path]
    if not path:
        path = '/'
    _queue = Queue()
    path2 = path.split(os.sep)
    path2 = path2[len(path2) - 1]
    data_layer.insert_peer()
    peer = data_layer.get_uuid_from_peer()
    data_layer.insert_data(id=1, file_name=path2, file_type='Folder', parent=path, generation=0, first=True,
                           peer=peer)
    for x in paths:
        path = x
        t = Thread(target=dfs, args=(path, _queue))
        t.start()
        t2 = Thread(target=save_to_disk, args=(data_layer, _queue, peer))
        t2.start()
        t.join()
        t2.join()
    start(get_paths())


def get_paths():
    path = '/media/roly/Extra'
    if not path:
        paths = ef.get_initials_paths()
    else:
        paths = [path]
    return paths


if __name__ == '__main__':
    print('----------- JF -----------')
    path = '/home/roly/file_system'
    paths = []
    if not path:
        paths = ef.get_initials_paths()
    else:
        paths = [path]
    password = getpass.getpass()
    while len(password) > 32:
        print('Password must be smaller than 32 characters')
        password = getpass.getpass()
    jump = 1
    data_layer = None
    if not path:
        path = '/'
    if not os.path.exists('./database.db'):
        jump = 0
        data_layer = data_layer_py.DataLayer('database.db')
        data_layer.create_databases()
        sha = hashlib.md5(password.encode())
        data_layer.insert_password(sha.hexdigest())
        _queue = Queue()
        path2 = path.split(os.sep)
        path2 = path2[len(path2) - 1]
        data_layer.insert_peer()
        peer = data_layer.get_uuid_from_peer()
        data_layer.insert_data(id=1, file_name=path2, file_type='Folder', parent=path, generation=0, first=True,
                               peer=peer)
        for x in paths:
            path = x
            t = Thread(target=dfs, args=(path, _queue))
            t.start()
            t2 = Thread(target=save_to_disk, args=(data_layer, _queue, peer))
            t2.start()
            t.join()
            t2.join()
    if not data_layer:
        data_layer = data_layer_py.DataLayer('database.db')
    while jump:
        u_p = data_layer.get_password()
        sha = hashlib.md5(password.encode())
        if sha.hexdigest() == u_p[1]:
            break
        password = getpass.getpass()
    # t4 = Thread(target=watch_layer.add_multi_platform_watch, args=(paths, Queue()))
    # t4.start()
    t5 = Thread(target=cl.start, args=())
    t5.start()
    # t6 = Thread(target=ed.start_observer, args=())
    # t6.start()
    while 1:
        print('Enter keywords:')
        words = input()
        cl.set_query(True)
        watch_layer.set_query(True)
        if not words.strip():
            continue
        for item in data_layer.find_data(words.split()):
            t = localtime(item[8])
            print('>Name: ' + str(item[2]) + '\n' + '>File Type: ' + str(item[4]) + '\n' + '>Address: '
                  + str(data_layer.get_address(item[1], item[7])) + '\n' + '>Machine: ' +
                  data_layer.get_peer_from_uuid(item[7]) + '\n' + '>Date: ' + str(t[0]) + '-' + str(t[1]) + '-' + str(
                t[2]) + '\n')
        print('Press any key for continue or write exit to finish')
        cl.set_query(False)
        watch_layer.set_query(False)
        end = input()
        if end.lower() == 'exit':
            break
    t4._stop()
    t5._stop()