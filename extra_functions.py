import string
import random

from Crypto.Cipher import AES

import data_layer_old


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


def copy_data(engine, lista, generation):
    for x in lista:
        if not x[0]:
            data_layer_old.insert_data(engine, x[1], x[2], x[3], generation=generation)
        else:
            data_layer_old.delete_data(engine, x[1])
    return len(lista)


