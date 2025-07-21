from flask import Flask, render_template, request, redirect, session, jsonify
from cryptography.fernet import Fernet
from datetime import timedelta
import os
import openai
import json
import requests

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

# Função para obter preços da Binance
def obter_precos_binance(par="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={par}"
        response = requests.get(url)

        if response.status_code != 200:
            return {"preco": "--", "variacao": "--", "volume": "--"}

        dados = response.json()
        return {
            "preco": dados.get("lastPrice", "--"),
            "variacao": dados.get("priceChangePercent", "--"),
            "volume": dados.get("volume", "--")
        }
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API da Binance: {e}")
        return {"preco": "--", "variacao": "--", "volume": "--"}

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
    
    dados = obter_precos_binance()  # Obter preços para exibição
    return render_template('painel_operacao.html', saldo=saldo_simulado, dados=dados)

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
        prompt = 'Analise o mercado BTC/USDT e diga se devemos COMPRAR, VENDER ou AGUARDAR.'
        openai.api_key = fernet.decrypt(chaves_armazenadas['openai'].encode()).decode()
        
        resposta = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[
                {"role": "system", "content": "Você é uma especialista em trading cripto. Responda com clareza e decisão."},
                {"role": "user", "content": prompt}
            ]
        )
        texto = resposta['choices'][0]['message']['content']
        return jsonify({'resposta': texto})
    except Exception as e:
        return jsonify({'erro': f'Erro IA: {e}'})

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

# 🔁 Inicializa chaves salvas
carregar_chaves_salvas()

if __name__ == '__main__':
    app.run(debug=True)