# src/connectivity/_crypto.py
from cryptolib import aes
from urandom import randint
import ure as re
import gc

gc.collect()

KEY_FILE_DIR = "cfg/crypto_key"

def pad(s:bytes, encoding:str='utf-8', pad_len:int=16):
    le = bytes(f'\r{len(s)}', encoding)
    sb = s + bytes([randint(32,127) for _ in range(pad_len - (len(s) + len(le)) % pad_len)]) + le
    while len(sb):
        yield sb[:16]
        sb = sb[16:]
    return sb

def get_aes() -> aes:
    with open(KEY_FILE_DIR, "r") as keyfile:
        return aes(keyfile.read(16), 1)

def encrypt(s:bytes|str, encoding="utf-8"):
    if isinstance(s, str):
        s = bytes(s, encoding)
    out = b''
    for part in pad(s, encoding):
        out += get_aes().encrypt(part)
    return out

def decrypt(s:bytes, pad_len:int=16):
    if not len(s) % pad_len == 0:
        raise ValueError(f"Encrypted string must be {pad_len} bytes. Got '{len(s)}'")
    out = b''
    for i in range(len(s) // pad_len):
        out += get_aes().decrypt(s[i * pad_len : (i+1) * pad_len])
    le = out.split(b'\r')[-1]
    return out[:int(le)]
