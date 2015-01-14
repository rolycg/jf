import string
import random

from Crypto.Cipher import AES

import data_layer


def random_string(length=16):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


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
    return AES.new(password)


def copy_data(engine, lista, generation):
    for x in lista:
        if not x[0]:
            data_layer.insert_data(engine, x[1], x[2], x[3], generation=generation)
        else:
            data_layer.delete_data(engine, x[1])
    return len(lista)



