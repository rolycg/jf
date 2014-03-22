import os
from queue import Queue
from threading import Thread


def dfs(path, q):
    for path, dirs, files in os.walk(path):
        q.put((path, dirs, files))


def save_to_disk(q):
    path, dirs, files = q.get()
    pass

if __name__ == '__main__':
    print('********** My Everything 2.0 **********')
    path = '/media/roly/Extra/Series'
    _queue = Queue()
    t = Thread(target=dfs, args=(path, _queue))
    t.start()

    t2 = Thread(target=save_to_disk, args=(_queue,))
    t2.start()

