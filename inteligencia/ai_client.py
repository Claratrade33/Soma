import os, re
from typing import List, Dict, Optional
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

SYSTEM_PROMPT = (
    "Você é a Clara, assistente de trading da ClaraVerse. "
    "Foque em gestão de risco, responda curto e sempre devolva uma quantidade numérica quando pedido."
)

def chat_responder(mensagem: str, contexto: Optional[List[Dict]] = None, modelo: str = "gpt-4o-mini") -> str:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    if contexto: msgs.extend(contexto)
    msgs.append({"role": "user", "content": mensagem})
    try:
        resp = client.chat.completions.create(model=modelo, messages=msgs)
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"[IA indisponível] {e}"

_QTY_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")

def sugerir_quantidade(symbol: str, preco: float, saldo_usdt: float, risco: str = "conservador") -> Dict:
    prompt = (
        f"Atue como risk manager.\n"
        f"Símbolo: {symbol}\nPreço: {preco:.8f} USDT\nSaldo: {saldo_usdt:.2f} USDT\n"
        f"Risco: {risco}. Use 1-5% (cons), 5-10% (mod), 10-20% (arrojado).\n"
        f"Retorne a quantidade do ativo (número) em uma linha isolada, e uma frase curta explicando."
    )
    texto = chat_responder(prompt)
    qty = None
    if texto and not texto.startswith("[IA indisponível]"):
        m = _QTY_RE.findall(texto)
        if m:
            try: qty = float(m[-1])
            except: qty = None
    return {"texto": texto, "qty": qty}