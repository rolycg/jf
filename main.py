import os
from queue import Queue
from threading import Thread
import data_layer

finished = True


def dfs(path, q):
    for path, dirs, files in os.walk(path):
        q.put((path, dirs, files))
    finished = False


def save_to_disk(engine, q, path):
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


if __name__ == '__main__':
    print('********** My Everything 2.0 **********')
    path = '/media/roly/Extra/Series/Modern Family'
    _queue = Queue()
    t = Thread(target=dfs, args=(path, _queue))
    t.start()
    engine = data_layer.create_database()
    t2 = Thread(target=save_to_disk, args=(engine, _queue, path))
    t2.start()

