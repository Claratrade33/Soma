from cryptography.fernet import Fernet
import os

# Caminho padrão onde as chaves serão salvas por usuário
KEYS_FOLDER = "keys"

# Cria pasta de chaves se não existir
os.makedirs(KEYS_FOLDER, exist_ok=True)

def gerar_chave(usuario):
    """Gera e salva uma chave única para o usuário"""
    chave = Fernet.generate_key()
    with open(f"{KEYS_FOLDER}/{usuario}.key", "wb") as chave_file:
        chave_file.write(chave)
    return chave

def carregar_chave(usuario):
    """Carrega chave de um usuário existente ou gera nova"""
    caminho = f"{KEYS_FOLDER}/{usuario}.key"
    if os.path.exists(caminho):
        with open(caminho, "rb") as chave_file:
            return chave_file.read()
    else:
        return gerar_chave(usuario)

def criptografar(texto, usuario):
    """Criptografa uma string com base na chave do usuário"""
    chave = carregar_chave(usuario)
    f = Fernet(chave)
    token = f.encrypt(texto.encode())
    return token.decode()

def descriptografar(token, usuario):
    """Descriptografa uma string com base na chave do usuário"""
    chave = carregar_chave(usuario)
    f = Fernet(chave)
    texto = f.decrypt(token.encode())
    return texto.decode()
