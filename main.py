import os
from queue import Queue
from threading import Thread
import data_layer
from time import sleep

finished = True
paint = False


def dfs(path, q):
    for path, dirs, files in os.walk(path):
        q.put((path, dirs, files))
    finished = False


def save_to_disk(engine, q, path):
    global paint
    path2 = path.split('/')
    path2 = path2[len(path2) - 1]
    data_layer.insert_data(engine, path2, 'Folder', path, True)
    while not q.empty() and finished:
        path, dirs, files = q.get()
        path = path.split('/')
        path = path[len(path) - 1]
        for x in dirs:
            data_layer.insert_data(engine=engine, file_name=x, file_type='Folder', paren=path)
        for x in files:
            data_layer.insert_data(engine=engine, file_name=x, file_type='Files', paren=path)
    paint = False


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
    path = '/media/roly/Extra/Series/Modern Family'
    _queue = Queue()
    t = Thread(target=dfs, args=(path, _queue))
    t.start()



    engine = data_layer.create_database()
    t2 = Thread(target=save_to_disk, args=(engine, _queue, path))
    t2.start()
    t3 = Thread(target=printing)
    t3.start()


