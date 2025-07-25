# clara_bunker.py (corrigido e completo)
import os
from cryptography.fernet import Fernet
from app import app, socketio

# Criptografia segura das chaves API
class BunkerSeguro:
    def __init__(self, arquivo_chave='chave_secreta.key'):
        self.arquivo_chave = arquivo_chave
        if not os.path.exists(arquivo_chave):
            chave = Fernet.generate_key()
            with open(arquivo_chave, 'wb') as f:
                f.write(chave)

    def carregar_chave(self):
        with open(self.arquivo_chave, 'rb') as f:
            return f.read()

    def criptografar(self, texto):
        chave = self.carregar_chave()
        f = Fernet(chave)
        return f.encrypt(texto.encode())

    def descriptografar(self, texto_criptografado):
        chave = self.carregar_chave()
        f = Fernet(chave)
        return f.decrypt(texto_criptografado).decode()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)