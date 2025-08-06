from clarinha_ia import solicitar_analise_json


def decide_and_execute(usuario_nome: str, client) -> dict:
    """Consulta a IA e executa uma ordem simples com salvaguardas."""
    analise = solicitar_analise_json()
    texto = analise.get("sugestao", "").lower()
    if "compra" in texto:
        side = "BUY"
    elif "venda" in texto:
        side = "SELL"
    else:
        return {"executado": False, "motivo": "Sem sinal claro", "analise": analise}

    quantidade = "0.001"
    try:
        order = client.create_order(symbol="BTCUSDT", side=side, type="MARKET", quantity=quantidade)
        return {"executado": True, "ordem": order, "analise": analise}
    except Exception as e:
        return {"executado": False, "erro": str(e), "analise": analise}
