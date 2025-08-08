from cryptography.fernet import Fernet
import os

KEYS_FOLDER = "keys"

# Garante que a pasta 'keys' existe
os.makedirs(KEYS_FOLDER, exist_ok=True)

def gerar_chave(usuario):
    """
    Gera uma chave Fernet exclusiva para o usuário e salva em /keys/usuario.key
    """
    chave = Fernet.generate_key()
    caminho = os.path.join(KEYS_FOLDER, f"{usuario}.key")
    with open(caminho, "wb") as f:
        f.write(chave)
    return chave

def carregar_chave(usuario):
    """
    Carrega a chave do usuário. Se não existir, cria.
    """
    caminho = os.path.join(KEYS_FOLDER, f"{usuario}.key")
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return f.read()
    return gerar_chave(usuario)

def criptografar(texto, usuario):
    """
    Criptografa o texto com a chave do usuário
    """
    chave = carregar_chave(usuario)
    f = Fernet(chave)
    return f.encrypt(texto.encode()).decode()

def descriptografar(token, usuario):
    """Descriptografa o token com a chave do usuário."""
    chave = carregar_chave(usuario)
    f = Fernet(chave)
    return f.decrypt(token.encode()).decode()
