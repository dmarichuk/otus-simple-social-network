import hashlib

def get_pwd_hash(pwd: str) -> bytes:
    return hashlib.sha256(pwd.encode()).digest()
