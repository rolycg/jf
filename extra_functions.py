import string
import random

from Crypto.Cipher import AES

import data_layer


def random_string(length=16):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


def get_cipher(password):
    return AES.new(password * 8)


def copy_data(engine, lista, generation):
    for x in lista:
        if not x[0]:
            data_layer.insert_data(engine, x[1], x[2], x[3], generation=generation)
        else:
            data_layer.delete_data(engine, x[1])
    return len(lista)


def get_max_generation():
    session = data_layer.get_session(data_layer.get_engine())
    return max([x[0] for x in session.query(data_layer.File.generation).all()])