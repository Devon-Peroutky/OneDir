from hashlib import md5
from binascii import b2a_base64
from random import choice


__hash_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&()*+,-./:;<=>?@[]^_`{|}~' 

def gen_hash(password, salt):
    """
    Creates a hash based on password and salt.
    @param password: plain text password.
    @param salt: a bunch of randomly generated chars.
    @return: the hashed password. 
    """
    split = len(salt)/2
    password = salt[:split] + password + salt[split:]
    password = b2a_base64(md5(password).digest()).strip()
    return password


def gen_salt():
    """
    Generates a 100 character long salt.
    @return: 100 character long salt.
    """
    salt = ''.join(choice(__hash_chars) for i in range(100))
    return salt
