import os
import time
import data_layer_old
from Crypto.Cipher import AES


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

import  re

if __name__ == '__main__':
    import socket
    cipher = AES.new('1234567891234567')
    cipher2 = AES.new('1234567891234568')
    a=cipher.encrypt('hola'*16)
    value = ('(212,dsdadasd,asdasd,sad,asd,fsdfsdf,dfsdfsdf)')
    elements = re.split(',+', value)
    elements[0] = elements[0][1:]
    elements[len(elements) - 1] = elements[len(elements) - 1][0:len(elements) - 1]
    print(elements)
    #print(extra_functions.random_string(16))
    import uuid
    print(str(uuid.uuid4()))
    print(socket.getfqdn())
    #print(socket.gethostbyname(socket.gethostname()))
    session = data_layer_old.get_session(data_layer_old.connect_database())
    generation = max(session.query(data_layer_old.File._id).all())
    #path = '/media/roly/Extra/Series/'
    #try_os_path(path)

    #q = queue.Queue()
    #t = threading.Thread(target=try_queue_put, args=(q,))
    #t2 = threading.Thread(target=try_queue_get, args=(q,))
    #t.start()
    #t2.start()

    #import sqlalchemy
    #print(sqlalchemy.__version__)

    # engine = data_layer.get_engine()
    # count = 0
    # for x in data_layer.get_database_all_elements(engine):
    #     count += 1
    # print(count)
    #
    # tim = time.time()
    # path = '/media/roly/Extra'
    # for _path, dirs, files in os.walk(path):
    #     pass
    # print(str(time.time() - tim))

    #import pyinotify
    #print(pyinotify.__version__)

    #printing()