import string
import random

from Crypto.Cipher import AES


def random_string(length=16):
    lst = [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
    str = "".join(lst)
    return str


def get_cipher(password):
    return AES.new(password * 8)