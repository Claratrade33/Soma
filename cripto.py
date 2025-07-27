from cryptography.fernet import Fernet
import os

class Cripto:
    def __init__(self, caminho_chave="chave_secreta.key"):
        if not os.path.exists(caminho_chave):
            chave = Fernet.generate_key()
            with open(caminho_chave, 'wb') as f:
                f.write(chave)
        else:
            with open(caminho_chave, 'rb') as f:
                chave = f.read()
        self.fernet = Fernet(chave)

    def criptografar(self, texto):
        return self.fernet.encrypt(texto.encode()).decode()

    def descriptografar(self, texto_criptografado):
        return self.fernet.decrypt(texto_criptografado.encode()).decode()