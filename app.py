from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from binance.client import Client as BinanceClient
import openai
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    binance_api_key = db.Column(db.String(200), nullable=True)
    binance_api_secret = db.Column(db.String(200), nullable=True)
    openai_api_key = db.Column(db.String(200), nullable=True)
    saldo_simulado = db.Column(db.Float, default=1000.0)

# Função para obter cliente Binance do usuário
def get_user_binance_client():
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user = User.query.get(user_id)
    if not user or not user.binance_api_key:
        return None
    
    return BinanceClient(user.binance_api_key, user.binance_api_secret)

# Função para obter dados públicos da Binance
def get_public_market_data():
    try:
        # Dados públicos da API da Binance
        ticker_url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        klines_url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=14"
        
        ticker_response = requests.get(ticker_url)
        ticker_data = ticker_response.json()
        
        klines_response = requests.get(klines_url)
        klines_data = klines_response.json()
        
        # Calcular RSI básico
        closes = [float(kline[4]) for kline in klines_data]
        rsi = calculate_rsi(closes)
        
        # Calcular suporte e resistência básicos
        high_prices = [float(kline[2]) for kline in klines_data]
        low_prices = [float(kline[3]) for kline in klines_data]
        
        return {
            'preco': ticker_data['lastPrice'],
            'variacao': ticker_data['priceChangePercent'],
            'volume': ticker_data['volume'],
            'rsi': round(rsi, 2),
            'suporte': round(min(low_prices), 2),
            'resistencia': round(max(high_prices), 2)
        }
    except Exception as e:
        return {
            'preco': '0',
            'variacao': '0',
            'volume': '0',
            'rsi': '50',
            'suporte': '0',
            'resistencia': '0'
        }

# Função para calcular RSI
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

# Rotas principais
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    return render_template("dashboard.html", user=user, saldo=user.saldo_simulado)

@app.route("/configurar", methods=["GET", "POST"])
def configurar():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == "POST":
        user.binance_api_key = request.form['binance_api_key']
        user.binance_api_secret = request.form['binance_api_secret']
        user.openai_api_key = request.form['openai_api_key']
        db.session.commit()
        flash('Chaves atualizadas com sucesso!')
        return redirect(url_for('dashboard'))
    
    return render_template("configurar.html", user=user)

# APIs do dashboard
@app.route("/api/dados_mercado")
def dados_mercado():
    return jsonify(get_public_market_data())

@app.route("/api/saldo")
def api_saldo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não logado'}), 401
    
    user = User.query.get(user_id)
    
    # Se tem chaves da Binance, tenta obter saldo real
    if user.binance_api_key:
        client = get_user_binance_client()
        if client:
            try:
                account_info = client.get_account()
                usdt_balance = next((item for item in account_info['balances'] if item['asset'] == 'USDT'), None)
                return jsonify({'saldo': usdt_balance['free'] if usdt_balance else '0'})
            except:
                pass
    
    # Retorna saldo simulado
    return jsonify({'saldo': str(user.saldo_simulado)})

@app.route("/api/sugestao_ia", methods=["POST"])
def sugestao_ia():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não logado'}), 401
    
    user = User.query.get(user_id)
    prompt = request.json.get('prompt', 'Analise o mercado BTC/USDT.')
    
    # Se tem chave OpenAI, usa a API real
    if user.openai_api_key:
        try:
            openai.api_key = user.openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            return jsonify({'resposta': response.choices[0].message.content})
        except Exception as e:
            return jsonify({'erro': str(e)}), 500
    
    # Resposta simulada
    respostas_simuladas = [
        "📊 Análise Técnica: BTC está em tendência lateral. RSI neutro indica equilíbrio. Aguarde rompimento para definir direção.",
        "🔍 Recomendação: Mercado em consolidação. Suporte forte identificado. Considere entrada em pullbacks.",
        "⚠️ Atenção: Volatilidade alta detectada. Gerencie risco adequadamente. Stop loss recomendado.",
        "📈 Sinal de Alta: RSI em sobrevenda, possível reversão. Alvo em resistência próxima."
    ]
    
    import random
    return jsonify({'resposta': random.choice(respostas_simuladas)})

@app.route("/api/executar_operacao", methods=["POST"])
def executar_operacao():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'erro': 'Usuário não logado'}), 401
    
    user = User.query.get(user_id)
    data = request.json
    tipo = data.get('tipo')
    quantidade = data.get('quantidade', 0.001)
    
    # Se tem chaves da Binance, tenta operação real
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
                
                return jsonify({'mensagem': f'{tipo.capitalize()} realizada com sucesso!', 'detalhes': order})
            except Exception as e:
                return jsonify({'erro': str(e)}), 500
    
    # Simulação de operação
    preco_atual = float(get_public_market_data()['preco'])
    valor_operacao = preco_atual * quantidade
    
    if tipo == 'comprar':
        user.saldo_simulado -= valor_operacao
        mensagem = f'Compra simulada realizada! -{valor_operacao:.2f} USDT'
    elif tipo == 'vender':
        user.saldo_simulado += valor_operacao
        mensagem = f'Venda simulada realizada! +{valor_operacao:.2f} USDT'
    else:
        return jsonify({'erro': 'Tipo de operação inválido'}), 400
    
    db.session.commit()
    return jsonify({'mensagem': mensagem})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)