import os, re
from typing import List, Dict
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = (
    "Você é a Clara, assistente de trading da ClaraVerse. "
    "Foque em gestão de risco, responda curto e sempre devolva uma quantidade numérica quando pedido."
)

def chat_responder(mensagem: str, contexto: List[Dict] | None = None, modelo: str = "gpt-4o-mini") -> str:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if contexto:
        msgs.extend(contexto)
    msgs.append({"role": "user", "content": mensagem})
    try:
        resp = openai.ChatCompletion.create(model=modelo, messages=msgs)
        return resp.choices[0].message.content
    except Exception as e:
        return f"[IA indisponível] {e}"

_QTY_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")

def sugerir_quantidade(symbol: str, preco: float, saldo_usdt: float, risco: str = "conservador") -> Dict:
    """
    Retorna um dicionário: {"texto": <explicação>, "qty": <float ou None>}
    """
    prompt = (
        f"Atue como risk manager.\n"
        f"Símbolo: {symbol}\nPreço atual: {preco:.8f} USDT\nSaldo disponível: {saldo_usdt:.2f} USDT\n"
        f"Perfil de risco: {risco} (conservador/moderado/arrojado)\n"
        f"Regras: use fração do saldo (ex: 1%-5% conservador, 5%-10% moderado, 10%-20% arrojado).\n"
        f"Retorne a quantidade de {symbol.replace('USDT','')} a comprar para ordem MARKET agora.\n"
        f"Formato: explique em 1 frase e informe a quantidade numa linha isolada, apenas o número."
    )
    texto = chat_responder(prompt)
    qty = None
    if texto and not texto.startswith("[IA indisponível]"):
        # pega o último número do texto
        nums = _QTY_RE.findall(texto)
        if nums:
            try:
                qty = float(nums[-1])
            except Exception:
                qty = None
    return {"texto": texto, "qty": qty}