import string
import random

from Crypto.Cipher import AES

import data_layer


def random_string(length=16):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


def unpad(string):
    res = ''
    for x in string:
        if not (x == '*' or x == ')' or x == ' '):
            res += x
    return res


def convert_to_str(data):
    res = '( ' + str(data[0]) + ', ' + str(data[1]) + ', ' + str(data[2]) + ', ' + str(data[3]) + ', ' + str(
        data[4]) + ')'
    if len(res) > 15 and not len(res) % 16:
        return res
    for x in range(0, 16 - (len(res) % 16)):
        res += '*'
    return res


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




