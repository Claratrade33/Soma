# services/crypto.py
import os, base64
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv("FERNET_KEY", "").strip()
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY não definida no ambiente. Defina no Render.")

# Validação explícita do formato
try:
    raw = base64.urlsafe_b64decode(FERNET_KEY.encode())
    if len(raw) != 32:
        raise ValueError("length != 32 bytes")
except Exception as e:
    raise RuntimeError(f"FERNET_KEY inválida: {e}")

fernet = Fernet(FERNET_KEY.encode())

def enc(texto: str) -> str:
    return fernet.encrypt(texto.encode()).decode()

def dec(token_str: str) -> str:
    return fernet.decrypt(token_str.encode()).decode()