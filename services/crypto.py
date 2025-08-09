import os
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY faltando no .env")

fernet = Fernet(FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY)

def enc(txt: str) -> str:
    return fernet.encrypt(txt.encode()).decode()

def dec(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()