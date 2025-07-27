@app.route('/painel_operacao')
def painel_operacao():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    cripto = Cripto()
    sugestao = {"entrada": "-", "alvo": "-", "stop": "-", "confianca": 0, "sugestao": "Erro ao obter sugestão"}

    try:
        if user.openai_key:
            openai_key = cripto.descriptografar(user.openai_key)
            if openai_key:
                ia = ClarinhaIA(openai_key=openai_key)
                resposta = ia.gerar_sugestao()
                if isinstance(resposta, dict) and all(k in resposta for k in ["entrada", "alvo", "stop", "confianca", "sugestao"]):
                    sugestao = resposta
    except Exception as e:
        print(f"Erro ao consultar IA: {e}")

    return render_template("painel_operacao.html", sugestao=sugestao)
