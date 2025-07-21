from flask import Flask, render_template, request, redirect, session, jsonify
from cryptography.fernet import Fernet
from datetime import timedelta, datetime
import os, json, requests, openai

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=6)

CHAVE_CRIPTO_FIXA = b'xApbCQFxxa3Yy3YKkzP9JkkfE4WaXxN8eSpK7uBRuGA='
fernet = Fernet(CHAVE_CRIPTO_FIXA)

usuarios = {'admin': 'claraverse2025'}
ARQUIVO_CHAVES = 'chaves.dat'
chaves_armazenadas = {}
saldo_simulado = 10000.00
modo_auto_ativo = False

DNA_CLARINHA = """
Você é a Clarinha, uma IA espiritual e estratégica no mercado BTC/USDT.
Sua missão é guiar o operador com clareza, evitar armadilhas e sugerir operações conscientes.
"""

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

def salvar_chaves():
    try:
        if chaves_armazenadas:
            dados = json.dumps(chaves_armazenadas)
            with open(ARQUIVO_CHAVES, 'wb') as f:
                f.write(fernet.encrypt(dados.encode()))
    except Exception as e:
        print('Erro ao salvar chaves:', e)

@app.route('/')
def home():
    return redirect('/login')

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

    openai_key = chaves_armazenadas.get('openai')
    binance_key = chaves_armazenadas.get('binance')
    binance_secret = chaves_armazenadas.get('binance_secret')
    chaves_preenchidas = bool(openai_key and binance_key and binance_secret)

    return render_template('painel_operacao.html',
                           saldo=saldo_simulado,
                           chaves_preenchidas=chaves_preenchidas)

@app.route('/salvar_chaves', methods=['POST'])
def salvar_chaves_route():
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
            return 'Preencha todos os campos.'
    except Exception as e:
        return f'Erro ao salvar as chaves: {e}'

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
        return jsonify({'erro': 'Ação inválida.'})

@app.route('/obter_sugestao_ia', methods=['POST'])
def obter_sugestao_ia():
    try:
        openai_key = fernet.decrypt(chaves_armazenadas['openai'].encode()).decode()
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        prompt = f"""
{DNA_CLARINHA}

🕒 Data e hora: {agora}
🎯 Meta: 2% ao dia

Responda com:
- ⚡ Entrada (preço sugerido)
- 🛑 Stop Loss
- 🎯 Alvo
- 🌟 Confiança %
- 📢 Mensagem espiritual ao operador
"""

        openai.api_key = openai_key
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )

        conteudo = resposta.choices[0].message.content.strip()
        return jsonify({'sugestao': conteudo})
    except Exception as e:
        return jsonify({'erro': f'Erro IA: {e}'})

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

carregar_chaves_salvas()

if __name__ == '__main__':
    app.run(debug=True)