import hashlib
import hmac
import time
import random
import json
import requests
from cryptography.fernet import Fernet
import os
import sys
import math
from threading import Thread, Lock
from queue import Queue
import base64
import zlib
import re

# ===== CONSTELATION PROTOCOL v2.0 =====
class QuantumEncryption:
    def __init__(self, cosmic_key=None):
        self.stellar_key = cosmic_key or Fernet.generate_key()
        self.cipher = Fernet(self.stellar_key)
        self.rotation_counter = 0

    def rotate_key(self):
        self.rotation_counter += 1
        if self.rotation_counter % 5 == 0:
            self.stellar_key = Fernet.generate_key()
            self.cipher = Fernet(self.stellar_key)

    def encrypt_data(self, data):
        nebula_data = json.dumps(data).encode()
        encrypted = self.cipher.encrypt(nebula_data)
        return base64.b85encode(zlib.compress(encrypted)).decode()

    def decrypt_data(self, encrypted_data):
        try:
            decoded = base64.b85decode(encrypted_data)
            decompressed = zlib.decompress(decoded)
            return json.loads(self.cipher.decrypt(decompressed).decode())
        except:
            return json.loads(self.cipher.decrypt(base64.b85decode(encrypted_data)).decode())

class CosmicObfuscator:
    @staticmethod
    def generate_quantum_signature(api_key, secret_key, payload):
        star_map = {
            'timestamp': int(time.time() * 1000),
            'nonce': random.randint(10**9, 10**10),
            'quantum': hashlib.sha3_256(os.urandom(1024)).hexdigest()[:24]
        }
        merged = {**payload, **star_map}
        keys = list(merged.keys())
        random.shuffle(keys)
        shuffled_params = {k: merged[k] for k in keys}

        query_string = '&'.join([
            f"{k}={v if random.random() > 0.3 else CosmicObfuscator._apply_fuzzing(v)}"
            for k, v in shuffled_params.items()
        ])

        signature = hmac.new(
            secret_key.encode(),
            query_string.encode(),
            hashlib.sha3_256
        ).hexdigest()

        return {**shuffled_params, 'signature': CosmicObfuscator._inject_noise(signature)}

    @staticmethod
    def _apply_fuzzing(value):
        if isinstance(value, (int, float)):
            return str(value) + random.choice(['', '.0', '.00'])
        elif isinstance(value, str):
            if random.random() > 0.7:
                return value + '/*' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=4)) + '*/'
            return value
        return value

    @staticmethod
    def _inject_noise(signature):
        noise_chars = ['-', '_', '~', '.']
        positions = sorted(random.sample(range(len(signature)), k=3))
        for pos in positions:
            signature = signature[:pos] + random.choice(noise_chars) + signature[pos:]
        return signature

# ===== ATIVAÇÃO DO BOT INVISÍVEL =====
class GalacticBot:
    def __init__(self):
        self.ativo = False
        self.thread = None

    def iniciar(self):
        if not self.ativo:
            self.ativo = True
            self.thread = Thread(target=self.executar)
            self.thread.daemon = True
            self.thread.start()
            print("🛡️ GalacticBot iniciado em modo invisível.")

    def executar(self):
        while self.ativo:
            tempo = random.uniform(3.0, 6.0)
            print("🔒 GalacticBot patrulhando silenciosamente...")
            time.sleep(tempo)

    def parar(self):
        self.ativo = False
        print("🛑 GalacticBot finalizado.")

# ===== FUNÇÃO DE INICIALIZAÇÃO EXPORTÁVEL =====
bot_global = GalacticBot()

def iniciar_galactic_bot():
    bot_global.iniciar()