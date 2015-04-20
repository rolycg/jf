import os
import multiprocessing


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





import time
from multiprocessing import Queue


def a():
    count = 10
    while count:
        print('Hi from ' + str(count))
        count -= 1
    print('a finish')


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

from queue import Empty
from Crypto.Cipher import AES
import base64


if __name__ == '__main__':
    aes = AES.new('1234567812345678')
    plaintext = aes.encrypt('*/!234-+12345678')
    print(plaintext)
    print(len(plaintext))
    a = base64.b64encode(plaintext)
    print(a)
    print(len(a))
    print(a.decode())
    print(len(a.decode()))
    b = base64.b64decode(a)
    print(b)
    print(len(b))





