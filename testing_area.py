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


if __name__ == '__main__':
    a = os.stat('/media/')






