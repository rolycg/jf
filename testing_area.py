import os
import queue
import time
import threading
import data_layer


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

if __name__ == '__main__':
    #path = '/media/roly/Extra/Series/'
    #try_os_path(path)

    #q = queue.Queue()
    #t = threading.Thread(target=try_queue_put, args=(q,))
    #t2 = threading.Thread(target=try_queue_get, args=(q,))
    #t.start()
    #t2.start()

    #import sqlalchemy
    #print(sqlalchemy.__version__)
    pass
    engine = data_layer.get_engine()
    count = 0
    for x in data_layer.get_database_all_elements(engine):
        count += 1
    print(count)

    #printing()

