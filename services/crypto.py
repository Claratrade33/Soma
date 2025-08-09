# services/crypto.py
import os
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv("FERNET_KEY", "").strip()
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY não definida no ambiente. Defina no Render.")

try:
    fernet = Fernet(FERNET_KEY.encode())
except Exception as e:
    raise RuntimeError(f"FERNET_KEY inválida: {e}")

def enc(texto: str) -> str:
    return fernet.encrypt(texto.encode()).decode()

def dec(token_str: str) -> str:
    return fernet.decrypt(token_str.encode()).decode()