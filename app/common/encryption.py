import os


def generate_aes_key():
    key = os.urandom(16)
    return key.hex().upper()
