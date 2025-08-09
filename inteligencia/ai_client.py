import os, re
from typing import List, Dict, Optional
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "Você é a Clara, assistente de trading da ClaraVerse. "
    "Foque em gestão de risco, responda curto e sempre devolva uma quantidade numérica quando pedido."
)

def chat_responder(mensagem: str, contexto: Optional[List[Dict]] = None, modelo: str = "gpt-4o-mini") -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if contexto:
        messages.extend(contexto)
    messages.append({"role": "user", "content": mensagem})
    try:
        resp = client.chat.completions.create(model=modelo, messages=messages)
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"[IA indisponível] {e}"

_QTY_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")

def sugerir_quantidade(symbol: str, preco: float, saldo_usdt: float, risco: str = "conservador") -> Dict:
    prompt = (
        f"Atue como risk manager.\n"
        f"Símbolo: {symbol}\nPreço atual: {preco:.8f} USDT\nSaldo disponível: {saldo_usdt:.2f} USDT\n"
        f"Perfil de risco: {risco} (conservador/moderado/arrojado).\n"
        f"Regras: use fração do saldo (1%-5% conservador, 5%-10% moderado, 10%-20% arrojado).\n"
        f"Retorne a quantidade de {symbol.replace('USDT','')} para ordem MARKET agora.\n"
        f"Explique em 1 frase e informe a quantidade numa linha isolada, apenas o número."
    )
    texto = chat_responder(prompt)
    qty = None
    if texto and not texto.startswith("[IA indisponível]"):
        nums = _QTY_RE.findall(texto)
        if nums:
            try:
                qty = float(nums[-1])
            except:
                qty = None
    return {"texto": texto, "qty": qty}