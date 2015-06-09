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

import os


def test():
    print('This way')


import argparse
import sys
import json

if __name__ == '__main__':
    print('\x1b[01;33m' + 'Note: ' + '\x1b[0m')
    a = json.dumps({str((1, 2, 3)): 'abc'})
    b = json.loads(a)
    for x in b.keys():
        print(x[1:len(x) - 1])
    # parser = argparse.ArgumentParser(description='Testing', prog=sys.argv[0])
    # parser.add_argument('query', metavar='q', type=str, help="query", nargs='*')
    # parse = parser.add_mutually_exclusive_group()
    # parse.add_argument('-c', '--create', nargs=1, help='Create a index from given address')
    # parse.add_argument('-m', '--more', nargs='?', help='More results', default=5)
    # parse.add_argument('-i', '--index', nargs='+', help='index devices')
    parser = argparse.ArgumentParser(description='JF: desktop finder for local networks', prog=sys.argv[0])
    parser.add_argument('query', metavar='q', type=str, help="Execute a query with arguments values", nargs='*')
    parse = parser.add_mutually_exclusive_group()
    parse.add_argument('-c', '--create', help='Create a index from given address', nargs='1', type=str)
    parse.add_argument('-m', '--more', help='Show more results', nargs='?', default=5)
    parse.add_argument('-i', '--index', help='Index a device', nargs='+')
    parser.add_argument('-f', help='Set a device', nargs='?')
    arg = parser.parse_args()
    print(arg)
    if arg.query:
        print('query ' + str(arg.query))
    if arg.more:
        print('More ' + str(arg.more))
    if arg.index:
        print('index ' + str(arg.index))
    if arg.create:
        print('Create ' + str(arg.create))
        #
        #     # data_obj = data_layer.DataLayer()
        # elements = "'deleted','New folder','C:Users\\\\Carlos\\\\Desktop\\\\WSGI'"
        # elements = ef.convert_to_tuple(elements)
        # elements = [x.strip()[1:-1] for x in elements]
        # if elements[0] == 'deleted':
        # data_obj.delete_data(elements[1], elements[2],
        #                          data_obj.get_id_from_uuid('c4dbd4c7-a826-45bf-a888-b3a9da34300a'))
        # elif elements[0] == 'updated':
        #     data_obj.update_data(elements[1:], data_obj.get_id_from_uuid('c4dbd4c7-a826-45bf-a888-b3a9da34300a'))
        #
        # aes = AES.new('1234567812345678')
        # plaintext = aes.encrypt('*/!234-+12345678')
        # print(plaintext)
        # print(len(plaintext))
        # a = base64.b64encode(plaintext)
        # print(a)
        # print(len(a))
        # print(a.decode())
        # print(len(a.decode()))
        # b = base64.b64decode(a)
        # print(b)
        # print(len(b))
