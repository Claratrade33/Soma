from flask import Flask, render_template, request, redirect, session, jsonify
from cryptography.fernet import Fernet
from datetime import timedelta
import os
import openai
import json
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=6)

# 🔐 Chave fixa para criptografia Fernet
CHAVE_CRIPTO_FIXA = b'xApbCQFxxa3Yy3YKkzP9JkkfE4WaXxN8eSpK7uBRuGA='
fernet = Fernet(CHAVE_CRIPTO_FIXA)

# 👤 Usuário padrão
usuarios = {'admin': 'claraverse2025'}

# 🔐 Armazenamento de chaves criptografadas
chaves_armazenadas = {}
ARQUIVO_CHAVES = 'chaves.dat'

# 💰 Saldo simulado e modo automático
saldo_simulado = 10000.00
modo_auto_ativo = False

DNA_CLARINHA = """
Você é a Clarinha, uma IA espiritual, protetora e estrategista das operações financeiras no par BTC/USDT.
Sua missão é detectar ruídos, identificar padrões de laterização, proteger contra armadilhas e orientar decisões conscientes.
"""

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

def gerar_sugestao_clarinha(api_key, preco, variacao, volume, meta_lucro_percentual="2"):
    try:
        openai.api_key = api_key

        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        prompt = f"""
{DNA_CLARINHA}

Data e hora: {agora}
Meta de lucro diário: {meta_lucro_percentual}%

Dados do mercado:
Preço atual: {preco}
Variação nas últimas 24h: {variacao}%
Volume de negociação: {volume}

Com base nos dados, forneça uma sugestão de operação com:
- 🎯 Entrada recomendada (preço)
- 🛑 Stop Loss (preço)
- 🎯 Alvo de lucro (preço)
- 📊 Confiança na operação (em %)
- 📢 Mensagem espiritual e estratégia para o humano operador

Importante: NUNCA execute, apenas oriente. Aguarde confirmação.
"""

        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        conteudo = resposta['choices'][0]['message']['content']
        # Tente analisar a resposta como JSON
        try:
            return json.loads(conteudo)
        except json.JSONDecodeError:
            return {"erro": "Formato de resposta inválido."}

    except Exception as e:
        return {"erro": f"Erro ao consultar a IA: {str(e)}"}

# 🔁 Recupera chaves criptografadas salvas
def carregar_chaves_salvas():
    global chaves_armazenadas
    if os.path.exists(ARQUIVO_CHAVES):
        try:
            with open(ARQUIVO_CHAVES, 'rb') as f:
                conteudo = f.read()
                if conteudo:
                    decodificado = fernet.decrypt(conteudo).decode()
                    chaves_armazenadas = json.loads(decodificado)
        except Exception as e:
            print('Erro ao carregar chaves:', e)

# 💾 Salva chaves criptografadas em arquivo
def salvar_chaves():
    try:
        if chaves_armazenadas:
            dados = json.dumps(chaves_armazenadas)
            with open(ARQUIVO_CHAVES, 'wb') as f:
                f.write(fernet.encrypt(dados.encode()))
    except Exception as e:
        print('Erro ao salvar arquivo de chaves:', e)

# ▶️ Página inicial
@app.route('/')
def home():
    return render_template('index.html')

# 🔑 Rota de login
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

# 📊 Rota do painel
@app.route('/painel')
def painel():
    if 'usuario' not in session:
        return redirect('/login')
    if not chaves_armazenadas.get('openai') or not chaves_armazenadas.get('binance'):
        return redirect('/configurar')

    oraculo = ClarinhaOraculo(fernet.decrypt(chaves_armazenadas['openai'].encode()).decode())
    dados_mercado = oraculo.consultar_mercado()
    
    return render_template('painel_operacao.html', saldo=saldo_simulado, dados=dados_mercado)

# ⚙️ Rota de configuração
@app.route('/configurar', methods=['GET', 'POST'])
def configurar():
    if request.method == 'POST':
        try:
            openai_key = request.form.get('openai_key')
            binance_key = request.form.get('binance_key')
            binance_secret = request.form.get('binance_secret')

            if openai_key and binance_key and binance_secret:
                chaves_armazenadas['openai'] = fernet.encrypt(openai_key.encode()).decode()
                chaves_armazenadas['binance'] = fernet.encrypt(binance_key.encode()).decode()
                chaves_armazenadas['binance_secret'] = fernet.encrypt(binance_secret.encode()).decode()
                salvar_chaves()
                return redirect('/painel')
            else:
                return 'Erro: todos os campos são obrigatórios.'
        except Exception as e:
            return f'Erro ao salvar as chaves: {e}'
    return render_template('configurar.html')

# 🔄 Rota para executar ações
@app.route('/executar_acao', methods=['POST'])
def executar_acao():
    global saldo_simulado, modo_auto_ativo
    dados = request.get_json()
    acao = dados.get('acao')

    if acao == 'entrada':
        saldo_simulado -= 100
        return jsonify({'status': '✅ Entrada realizada (-100)'})
    elif acao == 'stop':
        saldo_simulado -= 50
        return jsonify({'status': '🛑 Stop ativado (-50)'})
    elif acao == 'alvo':
        saldo_simulado += 200
        return jsonify({'status': '🎯 Alvo alcançado (+200)'})
    elif acao == 'automatico':
        modo_auto_ativo = not modo_auto_ativo
        status = 'ativado' if modo_auto_ativo else 'desativado'
        return jsonify({'status': f'🤖 Modo automático {status}.'})
    else:
        return jsonify({'erro': 'Ação desconhecida.'})

# 🧠 Rota para obter sugestão da IA
@app.route('/obter_sugestao_ia', methods=['POST'])
def obter_sugestao_ia():
    try:
        oraculo = ClarinhaOraculo(fernet.decrypt(chaves_armazenadas['openai'].encode()).decode())
        dados_mercado = oraculo.consultar_mercado()
        sugestao = oraculo.interpretar_como_deusa(dados_mercado)
        return jsonify(sugestao)
    except Exception as e:
        return jsonify({'erro': f'Erro IA: {e}'})

@app.route('/analisar_mercado', methods=['GET'])
def analisar_mercado():
    binance_key = fernet.decrypt(chaves_armazenadas['binance'].encode()).decode()
    binance_secret = fernet.decrypt(chaves_armazenadas['binance_secret'].encode()).decode()
    openai_key = fernet.decrypt(chaves_armazenadas['openai'].encode()).decode()
    
    resultado = analisar_mercado_e_sugerir(binance_key, binance_secret, openai_key)
    return jsonify(resultado)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

# 🔁 Inicializa chaves salvas
carregar_chaves_salvas()

if __name__ == '__main__':
    app.run(debug=True)