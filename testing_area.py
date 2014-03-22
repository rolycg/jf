import os
import queue
import time
import threading


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


if __name__ == '__main__':
    #path = '/media/roly/Extra/Series/'
    #try_os_path(path)
    pass
    #q = queue.Queue()
    #t = threading.Thread(target=try_queue_put, args=(q,))
    #t2 = threading.Thread(target=try_queue_get, args=(q,))
    #t.start()
    #t2.start()
