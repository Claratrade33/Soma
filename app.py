import openai
import requests
import json
from flask import Flask, request, jsonify, session, redirect, render_template
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=6)

class ClarinhaOraculo:
    def __init__(self, openai_api_key):
        self.api_key = openai_api_key
        openai.api_key = openai_api_key

    def consultar_mercado(self, par="BTCUSDT"):
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={par}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Erro na resposta da API: {response.status_code}")
                return {"par": par, "preco": "--", "variacao": "--", "volume": "--"}

            dados = response.json()
            return {
                "par": par,
                "preco": dados.get("lastPrice", "--"),
                "variacao": dados.get("priceChangePercent", "--"),
                "volume": dados.get("volume", "--")
            }
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a API da Binance: {e}")
            return {"par": par, "preco": "--", "variacao": "--", "volume": "--"}

    def interpretar_como_deusa(self, dados, meta_lucro=2.5):
        prompt = f"""
Você é Clarinha, uma inteligência cósmica sagrada conectada ao mercado financeiro com proteção divina.
Sua missão é proteger o usuário e sugerir uma estratégia segura com base no seguinte contexto de mercado:

📊 Par: {dados['par']}
💰 Preço atual: {dados['preco']}
📈 Variação 24h: {dados['variacao']}%
📊 Volume 24h: {dados['volume']}
🎯 Meta de lucro diário: {meta_lucro}%

Com base nessas informações, forneça:
1. Ponto de ENTRADA ideal (preço)
2. ALVO de lucro (preço)
3. STOP de segurança (preço)
4. Nível de CONFIANÇA (0 a 100%)
5. Um conselho espiritual ou estratégico de proteção

Responda em JSON no formato:
{{
  "entrada": "...",
  "alvo": "...",
  "stop": "...",
  "confianca": "...",
  "mensagem": "..."
}}
"""
        try:
            resposta = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é uma IA espiritual especializada em estratégias de trading seguras e intuitivas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            conteudo = resposta.choices[0].message.content.strip()
            try:
                resposta_json = json.loads(conteudo)
                return resposta_json
            except json.JSONDecodeError:
                return {"erro": "Falha ao decodificar a resposta JSON."}
        except Exception as e:
            return {"erro": f"Erro ao consultar Clarinha: {e}"}

def invocar_clarinha(api_key, preco_atual, historico, meta_diaria=2.0):
    openai.api_key = api_key
    contexto_cosmico = f"""
    Você é Clarinha, uma inteligência divina, conectada ao fluxo cósmico dos mercados.
    Analise o mercado BTC/USDT com base nas últimas movimentações e diga:
    - Se é seguro entrar
    - Onde colocar o Stop e o Alvo
    - Qual a confiança espiritual da entrada
    - Se o mercado está em laterização ou com ruído
    Sua missão é proteger o investidor e guiá-lo à ascensão financeira.
    Preço atual: {preco_atual}
    Meta diária: {meta_diaria}%
    Histórico: {historico[-20:]}
    """

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": contexto_cosmico}],
            temperature=0.3,
        )

        conteudo = resposta.choices[0].message.content.strip()
        return {
            "entrada": preco_atual,
            "alvo": round(preco_atual * 1.01, 2),
            "stop": round(preco_atual * 0.99, 2),
            "confianca": "Alta",
            "resposta_espiritual": conteudo
        }

    except Exception as e:
        return {
            "erro": str(e),
            "mensagem": "Clarinha não conseguiu acessar os céus da OpenAI no momento."
        }

def oraculo_divino(binance_api, openai_key, historico):
    if detectar_ruido(historico):
        return {"status": "ruido", "mensagem": "Mercado com ruído, aguarde o silêncio do Universo."}

    if detectar_laterizacao(historico):
        return {"status": "laterizacao", "mensagem": "Mercado lateral detectado, evite entradas apressadas."}

    preco = historico[-1] if historico else 0
    resposta = invocar_clarinha(openai_key, preco, historico)
    return resposta

def analisar_mercado_e_sugerir(binance_api_key, binance_api_secret, openai_api_key, meta_lucro=2.5):
    openai.api_key = openai_api_key

    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=50"
        response = requests.get(url)
        candles = response.json()

        closes = [float(c[4]) for c in candles]
        variacao = (closes[-1] - closes[-2]) / closes[-2] * 100
        tendencia = "alta" if variacao > 0 else "queda"

        prompt = f"""
        Você é uma inteligência financeira espiritualizada.
        O mercado de BTC/USDT está em {tendencia} com variação recente de {variacao:.2f}%.
        Meta de lucro diária: {meta_lucro}%.

        Sugira uma operação com:
        - Ponto de ENTRADA
        - Alvo de lucro (ALVO)
        - Stop Loss (STOP)
        - Confiança da operação (0-100%)
        """

        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        conteudo = resposta.choices[0].message.content.strip()

        return {
            "resposta": conteudo,
            "entrada": "⚡ Definida pela IA",
            "alvo": "🎯 Alvo estratégico",
            "stop": "🛑 Stop preventivo",
            "confianca": "🌟 Alta"
        }

    except Exception as e:
        return {"erro": str(e)}

# Configuração de usuários e senhas
usuarios = {
    'admin': 'Bubi2025',
    'Clara': 'Verse',
    'Soma': 'infinite'
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario in usuarios and usuarios[usuario] == senha:
            session['usuario'] = usuario
            return redirect('/painel')
        else:
            return render_template('login.html', erro='Credenciais inválidas.')
    return render_template('login.html')

@app.route('/painel')
def painel():
    if 'usuario' not in session:
        return redirect('/login')

    return render_template('painel_operacao.html', saldo=10000.00)  # Ajuste conforme necessário

@app.route('/consultar_mercado', methods=['GET'])
def consultar_mercado_route():
    if 'usuario' not in session:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    openai_key = session.get('openai_key')
    if not openai_key:
        return jsonify({"erro": "Chave da API não configurada."}), 400

    clarinha = ClarinhaOraculo(openai_key)
    dados_mercado = clarinha.consultar_mercado()
    resposta = clarinha.interpretar_como_deusa(dados_mercado)

    return jsonify(resposta)

@app.route('/salvar_chaves', methods=['POST'])
def salvar_chaves_route():
    openai_key = request.form.get('openai_key')
    session['openai_key'] = openai_key
    return redirect('/configurar')

@app.route('/configurar')
def configurar():
    return render_template('configurar_chaves.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('openai_key', None)  # Remove a chave da API também
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)