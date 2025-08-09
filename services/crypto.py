# services/crypto.py
import os
import base64
from cryptography.fernet import Fernet, InvalidToken

__all__ = ["enc", "dec", "validate_fernet_env"]

_FERNET = None
_LAST_ERR = ""

def _build_fernet():
    """Cria e cacheia o objeto Fernet a partir da env FERNET_KEY."""
    global _FERNET, _LAST_ERR
    key = (os.getenv("FERNET_KEY") or "").strip()
    if not key:
        _LAST_ERR = "FERNET_KEY ausente no ambiente."
        _FERNET = None
        return

    try:
        raw = base64.urlsafe_b64decode(key.encode())
        if len(raw) != 32:
            _LAST_ERR = "FERNET_KEY inválida: tamanho ≠ 32 bytes após base64."
            _FERNET = None
            return
        _FERNET = Fernet(key.encode())
        _LAST_ERR = ""
    except Exception as e:
        _FERNET = None
        _LAST_ERR = f"FERNET_KEY inválida: {e}"

def validate_fernet_env():
    """
    Verifica se há FERNET_KEY válida no ambiente.
    Retorna (ok: bool, msg: str)
    """
    if _FERNET is None and not _LAST_ERR:
        _build_fernet()
    if _FERNET is None:
        return False, _LAST_ERR or "FERNET_KEY não configurada."
    return True, ""

def enc(plaintext: str) -> bytes:
    """Criptografa string para bytes seguros."""
    if _FERNET is None:
        _build_fernet()
    if _FERNET is None:
        raise RuntimeError(_LAST_ERR or "FERNET_KEY não configurada.")
    return _FERNET.encrypt(plaintext.encode())

def dec(token: bytes) -> str:
    """Descriptografa bytes para string."""
    if _FERNET is None:
        _build_fernet()
    if _FERNET is None:
        raise RuntimeError(_LAST_ERR or "FERNET_KEY não configurada.")
    try:
        return _FERNET.decrypt(token).decode()
    except InvalidToken:
        raise RuntimeError("Token inválido para esta FERNET_KEY.")