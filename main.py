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
    data_layer.insert_data(engine, os.path.basename(path), 'Folder', os.path.dirname(path))
    while not q.empty() and finished:
        if q.empty():
            pass
        path, dirs, files = q.get()
        for x in dirs:
            data_layer.insert_data(engine=engine, file_name=x, file_type='Folder', paren=path)
        for x in files:
            data_layer.insert_data(engine=engine, file_name=x, file_type='File', paren=path)


if __name__ == '__main__':
    print('********** My Everything 2.0 **********')
    path = '/media/roly/Extra/Series/Monk/'
    _queue = Queue()
    t = Thread(target=dfs, args=(path, _queue))
    t.start()
    engine = data_layer.__create_database__()
    t2 = Thread(target=save_to_disk, args=(engine, _queue, path))
    t2.start()

