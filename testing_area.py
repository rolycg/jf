import os


def try_os_path(path):
    for pathname, dirname, filename in os.walk(path):
        print(pathname + ':')
        print('\tFolders:')
        for x in dirname:
            print('\t\t' + x)
        print('\tFiles:')
        for x in filename:
            print('\t\t' + x)


def try_queue_put(my_queue):
    while 1:
        my_queue.put(1)
        time.sleep(1)


def try_queue_get(my_queue):
    while 1:
        tmp = my_queue.get()
        print(tmp)
        time.sleep(0.5)


paint = True


def printing():
    count = 0
    while paint:
        if count % 3 == 0:
            print('Indexing.', end='\r')
            count += 1
            time.sleep(0.5)
        elif count % 3 == 1:
            print('Indexing..', end='\r')
            count += 1
            time.sleep(0.5)
        if count % 3 == 2:
            print('Indexing...', end='\r')
            count += 1
            time.sleep(0.5)
    print('', end='\r')


import time
import threading
from queue import Empty, Queue

c = 'it works'
q = Queue()


def a():
    global c
    global q
    while 1:
        q.put('I am A')
        time.sleep(0.2)


def b():
    global q
    global c
    while 1:
        time.sleep(2)
        try:
            if not q.empty():
                a = q.get(timeout=2)
                if a:
                    print(a)
        except Empty:
            print(c)
            continue


if __name__ == '__main__':
    t = threading.Thread(target=a, args=())
    t.start()
    b()
    while 1:
        time.sleep(20)
        try:
            pass
            t._stop()
            t2._stop()
        except AssertionError:
            pass
        print('Lo mate')
        break






