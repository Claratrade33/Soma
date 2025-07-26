from flask import jsonify

@app.route('/executar_ordem', methods=["POST"])
def executar_ordem():
    user = get_current_user()
    if not user:
        return jsonify({"status": "erro", "erro": "Usuário não autenticado"})

    data = request.get_json()
    tipo = data.get("tipo")

    try:
        client = Client(user.api_key, user.api_secret)

        if tipo == "entrada":
            client.order_market_buy(symbol="BTCUSDT", quantity=0.001)
            return jsonify({"status": "ok", "mensagem": "Ordem de entrada executada."})

        elif tipo == "stop":
            return jsonify({"status": "ok", "mensagem": "Stop acionado (simulado)."})

        elif tipo == "alvo":
            return jsonify({"status": "ok", "mensagem": "Alvo atingido (simulado)."})

        elif tipo == "automatico":
            from threading import Thread
            from clarinha_ia import ClarinhaIA, loop_automatico
            ia = ClarinhaIA(api_key=user.api_key, api_secret=user.api_secret, openai_key=user.openai_key)
            t = Thread(target=loop_automatico, args=(ia, client))
            t.daemon = True
            t.start()
            return jsonify({"status": "ok", "mensagem": "Modo automático ativado."})

        else:
            return jsonify({"status": "erro", "erro": "Tipo de ordem desconhecida"})

    except Exception as e:
        return jsonify({"status": "erro", "erro": str(e)})