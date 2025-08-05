from cryptography.fernet import Fernet
import os

KEYS_FOLDER = "keys"
os.makedirs(KEYS_FOLDER, exist_ok=True)

def gerar_chave(usuario):
    chave = Fernet.generate_key()
    with open(f"{KEYS_FOLDER}/{usuario}.key", "wb") as chave_file:
        chave_file.write(chave)
    return chave

def carregar_chave(usuario):
    caminho = f"{KEYS_FOLDER}/{usuario}.key"
    if os.path.exists(caminho):
        with open(caminho, "rb") as chave_file:
            return chave_file.read()
    else:
        return gerar_chave(usuario)

def criptografar(texto, usuario):
    chave = carregar_chave(usuario)
    f = Fernet(chave)
    return f.encrypt(texto.encode()).decode()

def descriptografar(token, usuario):
    chave = carregar_chave(usuario)
    f = Fernet(chave)
    return f.decrypt(token.encode()).decode()