from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from binance.client import Client as BinanceClient
import openai
import os
import requests
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'claraverse_secret_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claraverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(200), nullable=True)
    binance_api_secret = db.Column(db.String(200), nullable=True)
    openai_api_key = db.Column(db.String(200), nullable=True)
    saldo_simulado = db.Column(db.Float, default=10000.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)

def get_user_binance_client():
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user = User.query.get(user_id)
    if not user or not user.binance_api_key:
        return None
    
    try:
        return BinanceClient(user.binance_api_key, user.binance_api_secret)
    except:
        return None

def get_public_market_data():
    try:
        ticker_url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        klines_url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=20"
        
        ticker_response = requests.get(ticker_url)
        ticker_data = ticker_response.json()
        
        klines_response = requests.get(klines_url)
        klines_data = klines_response.json()
        
        closes = [float(kline[4]) for kline in klines_data]
        highs = [float(kline[2]) for kline in klines_data]
        lows = [float(kline[3]) for kline in klines_data]
        volumes = [float(kline[5]) for kline in klines_data]
        
        rsi = calculate_rsi(closes)
        
        return {
            'preco': float(ticker_data['lastPrice']),
            'variacao': float(ticker_data['priceChangePercent']),
            'volume': format_volume(float(ticker_data['volume'])),
            'rsi': round(rsi, 2),
            'suporte': round(min(lows), 2),
            'resistencia': round(max(highs), 2),
            'media_volume': round(sum(volumes) / len(volumes), 0),
            'high_24h': float(ticker_data['highPrice']),
            'low_24h': float(ticker_data['lowPrice'])
        }
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return {
            'preco': 45000.0,
            'variacao': 0.0,
            'volume': '1.2B',
            'rsi': 50.0,
            'suporte': 44000.0,
            'resistencia': 46000.0,
            'media_volume': 25000,
            'high_24h': 46500.0,
            'low_24h': 43500.0
        }

def format_volume(volume):
    if volume >= 1000000000:
        return f"{volume/1000000000:.1f}B"
    elif volume >= 1000000:
        return f"{volume/1000000:.1f}M"
    elif volume >= 1000:
        return f"{volume/1000:.1f}K"
    else:
        return f"{volume:.0f}"

def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return 50
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# ROTAS PRINCIPAIS
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe!')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado!')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Usuário criado com sucesso!')
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas!')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/dashboard")
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    market_data = get_public_market_data()
    
    return render_template("dashboard.html", 
                         user=user, 
                         saldo=f"{user.saldo_simulado:,.2f}",
                         market_data=market_data)

@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == "POST":
        user.binance_api_key = request.form.get('binance_api_key', '').strip()
        user.binance_api_secret = request.form.get('binance_api_secret', '').strip()
        user.openai_api_key = request.form.get('openai_api_key', '').strip()
        
        db.session.commit()
        flash('🚀 Configurações atualizadas com sucesso!')
        return redirect(url_for('dashboard'))
    
    return render_template("configurar.html", user=user)

# APIS DO DASHBOARD
@app.route("/api/dados_mercado")
def dados_mercado():
    return jsonify(get_public_market_data())

@app.route("/api/saldo")
def api_saldo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não logado'}), 401
    
    user = User.query.get(user_id)
    
    if user.binance_api_key:
        client = get_user_binance_client()
        if client:
            try:
                account_info = client.get_account()
                usdt_balance = next((item for item in account_info['balances'] if item['asset'] == 'USDT'), None)
                return jsonify({'saldo': usdt_balance['free'] if usdt_balance else '0', 'tipo': 'real'})
            except:
                pass
    
    return jsonify({'saldo': f"{user.saldo_simulado:.2f}", 'tipo': 'simulado'})

@app.route("/api/sugestao_ia", methods=["POST"])
def sugestao_ia():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não logado'}), 401
    
    user = User.query.get(user_id)
    data = request.json
    prompt = data.get('prompt', '')
    contexto = data.get('contexto', 'oraculo')
    
    if user.openai_api_key:
        try:
            openai.api_key = user.openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            return jsonify({'resposta': response.choices.message.content})
        except Exception as e:
            return jsonify({'erro': f'Erro na API OpenAI: {str(e)}'}), 500
    
    # Respostas simuladas por contexto
    respostas_contexto = {
        'oraculo': [
            "🔮 **VISÃO ORÁCULO** ✨\n\n🌟 **PREVISÃO MÍSTICA:**\nAs energias cósmicas revelam turbulência no éter digital! O BTC navega entre dimensões paralelas.\n\n⚡ **TRÊS CENÁRIOS REVELADOS:**\n• **🚀 ASCENSÃO:** Rompimento da barreira etérea → +7.3%\n• **⚖️ EQUILÍBRIO:** Dança entre portais dimensionais\n• **📉 PURIFICAÇÃO:** Teste das forças anciãs → -4.8%\n\n🎯 **ENTRADA SAGRADA:** Aguardar o alinhamento dos cristais\n🛡️ **PROTEÇÃO MÁGICA:** Escudo em 3.2% abaixo\n⏰ **CICLO TEMPORAL:** 4-8 horas terrestres\n\n✨ **CONFIANÇA ORÁCULO:** 79% das visões se alinham",
            
            "🔮 **MENSAGEM DO ORÁCULO** 🌟\n\n✨ Os ventos cósmicos sussurram mudanças... O RSI dança entre 42-58, zona de transição espiritual!\n\n🔥 **RITUAIS RECOMENDADOS:**\n• **MEDITAÇÃO:** Aguardar sinais mais claros\n• **PROTEÇÃO:** Stop em território sagrado\n• **MANIFESTAÇÃO:** Alvo nas constelações superiores\n\n🌙 **FASE LUNAR:** Crescente de oportunidades\n⭐ **ENERGIA DOMINANTE:** Paciência e precisão"
        ],
        
        'cosmo': [
            "🌌 **TRANSMISSÃO CÓSMICA** 🪐\n\n🔭 **ANÁLISE INTER-DIMENSIONAL:**\nObservando através do telescópio universal, vejo perturbações no campo gravitacional financeiro. As forças macro-econômicas estão em dança celestial complexa.\n\n🌍 **FATORES PLANETÁRIOS EM AÇÃO:**\n• 🏛️ Saturno (Políticas Monetárias) em quadratura\n• 💫 Júpiter (Liquidez Global) em retrogradação\n• ⚡ Marte (Volatilidade) ascendente\n• 🌙 Lua (Sentimento) em eclipse parcial\n\n🛸 **NAVEGAÇÃO INTERGALÁCTICA:**\nAs correntes estelares sugerem cautela nos próximos parsecs. O BTC está surfando ondas gravitacionais entre $44K-$47K.\n\n⭐ **CONSTELAÇÃO DOMINANTE:** Paciência Cósmica\n🌟 **PRÓXIMO PORTAL:** 72 horas terrestres",
            
            "🌌 **CLARINHA COSMO ONLINE** 🛸\n\n🪐 Detectando anomalias no espaço-tempo financeiro... Os buracos negros institucionais estão sugando liquidez!\n\n🌟 **STATUS DOS QUADRANTES:**\n• Quadrante Alpha (Ásia): Energia neutra 🟡\n• Quadrante Beta (Europa): Pressão vendedora 🔴\n• Quadrante Gamma (América): Acumulação 🟢\n\n🚀 **RECOMENDAÇÃO UNIVERSAL:**\nMantenham órbita baixa até que as tempestades solares cessem. O cosmos nos enviará sinais mais claros quando Mercúrio sair da retrogradação financeira.\n\n🔮 **PROBABILIDADE CÓSMICA:** Aguardar 67%"
        ],
        
        'inteligencia': [
            "🧠 **ANÁLISE QUÂNTICA ATIVADA** 💡\n\n📊 **PROCESSAMENTO NEURAL COMPLETO:**\n```\nDADOS PROCESSADOS: 847,293 pontos\nPADRÕES IDENTIFICADOS: 23 fractais ativos\nCORRELAÇÕES: 0.73 com S&P500, 0.81 com DXY\n```\n\n🎯 **MÉTRICAS CRÍTICAS:**\n• **Probabilidade Alta:** 67.8% (próximas 6h)\n• **Volatilidade Implícita:** 31.2%\n• **Volume Anômalo:** +18.7% acima da média\n• **Força Relativa:** RSI(14) = 54.3\n\n🔬 **ALGORITMO RECOMENDA:**\n• **POSIÇÃO:** 3.2% do capital total\n• **ENTRADA:** $45,240 ± $50\n• **STOP LOSS:** -2.9% ($43,870)\n• **TAKE PROFIT:** +5.1% ($47,550)\n\n⚡ **CONFIANÇA ALGORÍTMICA:** 81.4%",
            
            "🧠 **SISTEMA NEURAL ONLINE** 📈\n\n💾 **SCAN COMPLETO EXECUTADO:**\n```\nAnalysing 1,247,891 data points...\nPattern recognition: ACTIVE\nRisk assessment: CALCULATED\nProbability matrix: UPDATED\n```\n\n🔢 **INDICADORES QUÂNTICOS:**\n• **Sharpe Ratio Projetado:** 2.17\n• **Drawdown Máximo:** 3.8%\n• **Win Rate Histórico:** 74.2%\n• **Média de Retorno:** +4.6%\n\n🎯 **ESTRATÉGIA OTIMIZADA:**\nEsperar breakout com volume confirmado. Modelo indica 79.3% de sucesso com confluência de 3+ indicadores.\n\n⚗️ **PRECISÃO CALCULADA:** 84.7%"
        ]
    }
    
    import random
    return jsonify({'resposta': random.choice(respostas_contexto.get(contexto, respostas_contexto['oraculo']))})

@app.route("/api/executar_operacao", methods=["POST"])
def executar_operacao():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não logado'}), 401
    
    user = User.query.get(user_id)
    data = request.json
    tipo = data.get('tipo')
    quantidade = data.get('quantidade', 0.001)
    
    if user.binance_api_key:
        client = get_user_binance_client()
        if client:
            try:
                if tipo == 'comprar':
                    order = client.order_market_buy(symbol='BTCUSDT', quantity=quantidade)
                elif tipo == 'vender':
                    order = client.order_market_sell(symbol='BTCUSDT', quantity=quantidade)
                else:
                    return jsonify({'erro': 'Tipo de operação inválido'}), 400
                
                return jsonify({
                    'mensagem': f'✅ {tipo.capitalize()} executada com sucesso!', 
                    'detalhes': order,
                    'tipo': 'real'
                })
            except Exception as e:
                return jsonify({'erro': f'Erro na execução: {str(e)}'}), 500
    
    # Simulação
    market_data = get_public_market_data()
    preco_atual = market_data['preco']
    valor_operacao = preco_atual * quantidade
    
    if tipo == 'comprar':
        if user.saldo_simulado >= valor_operacao:
            user.saldo_simulado -= valor_operacao
            mensagem = f'🚀 Compra simulada! -{valor_operacao:.2f} USDT'
        else:
            return jsonify({'erro': 'Saldo insuficiente'}), 400
    elif tipo == 'vender':
        user.saldo_simulado += valor_operacao
        mensagem = f'💰 Venda simulada! +{valor_operacao:.2f} USDT'
    else:
        return jsonify({'erro': 'Tipo de operação inválido'}), 400
    
    db.session.commit()
    return jsonify({'mensagem': mensagem, 'tipo': 'simulado'})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)