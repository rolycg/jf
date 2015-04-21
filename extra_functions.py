import string
import random
import os
import sys
from ctypes import *

from Crypto.Cipher import AES

import data_layer


def random_string(length=16):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


def convert_to_tuple(chain):
    return chain.split(',')


def unpad(string, b=1):
    res = ''
    if b:
        for x in string:
            if not (x == '*' or x == ')' or x == ' '):
                res += x
    else:
        for x in string:
            if not (x == '*' or x == ')'):
                res += x
    return res


def convert_to_str(data):
    res = ''
    if isinstance(data, tuple):
        res = '( ' + str(data[1]) + '? ' + str(data[2]) + '? ' + str(data[3]) + '? ' + str(data[4]) + '? ' + str(
            data[5]) + '? ' + str(data[6]) + '? ' + str(data[7]) + '?' + str(data[8]) + ')'
    else:
        res = data
    if len(res) > 15 and not len(res) % 16:
        return res.encode(encoding='LATIN-1')
    for x in range(0, 16 - (len(res) % 16)):
        res += '*'
    try:
        return res.encode(encoding='LATIN-1')
    except UnicodeEncodeError:
        return res.encode(encoding='utf_32')


def get_cipher(password):
    if len(password) <= 16:
        for x in range(0, 16 - len(password)):
            password += '*'
    elif len(password) <= 24:
        for x in range(0, 24 - len(password)):
            password += '*'
    else:
        for x in range(0, 32 - len(password)):
            password += '*'

    aes = AES.new(password)
    return aes


def check_paths(list_parents, real_path, peer):
    data_obj = data_layer.DataLayer('database.db')
    for j in range(0, len(real_path)):
        path = real_path[j]
        tmp = []
        for i in range(0, len(list_parents)):
            if path != list_parents[i]:
                list_parents.remove(i)
            else:
                for x in data_obj.cursor.execute('SELECT * FROM File WHERE name_ext=? AND machine=?',
                                                 (list_parents[i], peer)):
                    tmp.append(x[1])

        if len(list_parents) == 1:
            return list_parents[0]
        list_parents = tmp


def split_paths(path):
    try:
        tmp = path.decode().split(os.sep)
    except AttributeError:
        tmp = path.split(os.sep)
    if not tmp[0]:
        tmp[0] = os.sep
    return tmp


class Cache():
    def __init__(self, limit=1000):
        self.limit = limit
        self.cache = []

    def append(self, element):
        self.cache.append(element)

    def __getitem__(self, item):
        return self.cache[item]

    def clear(self):
        self.cache.clear()

    def __len__(self):
        return self.cache.__len__()

    def __iter__(self):
        return self.cache.__iter__()


def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives


def get_initials_paths():
    o_s = sys.platform
    if o_s.startswith('linux'):
        return ['/']
    elif o_s.startswith('win32'):
        return get_drives()
    elif o_s.startswith('darwin'):
        return ['/']


def get_date(path):
    return os.stat(path)[7]


def convert_message(messages):
    ret = ''
    for x in messages:
        ret += x + '\n'
    return ret


if __name__ == '__main__':
    print((get_date('/media/roly/Extra/Series/')))
    print((get_date('/media/roly/Extra/Work/')))
