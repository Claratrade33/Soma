from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from binance.client import Client as BinanceClient
import openai
import os
import requests
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_quantum_secret_2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELO DE USUÁRIO
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

# DECORADOR DE PROTEÇÃO DE ROTAS
def login_required(f):
    """Decorador para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página!', 'warning')
            return redirect(url_for('login'))
        
        # Verificar se usuário ainda existe no banco
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            flash('Sessão inválida. Faça login novamente.', 'error')
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def create_default_users():
    """Cria usuários padrão do sistema"""
    default_users = [
        {
            'username': 'admin',
            'email': 'admin@claraverse.com',
            'password': 'Bubi2025',
            'saldo': 15000.0,
            'is_premium': True
        },
        {
            'username': 'Clara',
            'email': 'clara@claraverse.com', 
            'password': 'Verse',
            'saldo': 25000.0,
            'is_premium': True
        },
        {
            'username': 'Soma',
            'email': 'soma@claraverse.com',
            'password': 'infinite',
            'saldo': 50000.0,
            'is_premium': True
        }
    ]
    
    for user_data in default_users:
        # Verificar se usuário já existe
        existing_user = User.query.filter_by(username=user_data['username']).first()
        
        if not existing_user:
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                saldo_simulado=user_data['saldo'],
                is_premium=user_data['is_premium']
            )
            db.session.add(new_user)
    
    try:
        db.session.commit()
        print("✅ Usuários padrão criados com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar usuários: {e}")

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
        
        ticker_response = requests.get(ticker_url, timeout=10)
        ticker_data = ticker_response.json()
        
        klines_response = requests.get(klines_url, timeout=10)
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
            'preco': 95247.50,
            'variacao': 2.35,
            'volume': '1.2B',
            'rsi': 62.4,
            'suporte': 93500.0,
            'resistencia': 96500.0,
            'media_volume': 35000,
            'high_24h': 96500.0,
            'low_24h': 93500.0
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
    """Rota principal - redireciona conforme autenticação"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Rota de registro com validação aprimorada"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validação de entrada
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template("register.html")
        
        # Validação de username
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            flash('Username deve conter apenas letras, números e underscore!', 'error')
            return render_template("register.html")
        
        # Validação de email
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Email inválido!', 'error')
            return render_template("register.html")
        
        # Verificar duplicatas
        if User.query.filter_by(username=username).first():
            flash('Username já existe! Escolha outro.', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado! Use outro email.', 'error')
            return render_template("register.html")
        
        try:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            
            flash('🎉 Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')
            return render_template("register.html")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Rota de login com suporte a username ou email"""
    # Se já estiver logado, redirecionar
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        login_field = request.form.get('username', '').strip()  # Pode ser username ou email
        password = request.form.get('password', '')
        
        # Validação básica
        if not login_field or not password:
            flash('Login e senha são obrigatórios!', 'error')
            return render_template("login.html")
        
        try:
            # Buscar por username ou email
            user = User.query.filter(
                (User.username == login_field) | (User.email == login_field)
            ).first()
            
            if user and check_password_hash(user.password, password):
                # Login bem-sucedido - criar sessão segura
                session.permanent = True
                session['user_id'] = user.id
                session['username'] = user.username
                session['logged_in'] = True
                
                flash(f'🚀 Bem-vindo(a), {user.username}!', 'success')
                
                # Redirecionar para página solicitada ou dashboard
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            else:
                flash('🚫 Login ou senha incorretos!', 'error')
                
        except Exception as e:
            flash('Erro no sistema. Tente novamente.', 'error')
            print(f"Erro no login: {e}")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Rota de logout segura"""
    username = session.get('username', 'Usuário')
    session.clear()
    flash(f'👋 Até logo, {username}!', 'info')
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard principal - protegido por decorador"""
    user = User.query.get(session['user_id'])
    market_data = get_public_market_data()
    
    return render_template("dashboard.html", 
                         user=user, 
                         saldo=f"{user.saldo_simulado:,.2f}",
                         market_data=market_data)

@app.route("/configurar", methods=["GET", "POST"])
@login_required
def configurar():
    """Rota de configurações - protegida"""
    user = User.query.get(session['user_id'])
    
    if request.method == "POST":
        try:
            # Sanitizar entrada
            user.binance_api_key = request.form.get('binance_api_key', '').strip()
            user.binance_api_secret = request.form.get('binance_api_secret', '').strip()
            user.openai_api_key = request.form.get('openai_api_key', '').strip()
            
            db.session.commit()
            flash('🚀 Configurações atualizadas com sucesso!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao salvar configurações. Tente novamente.', 'error')
    
    return render_template("configurar.html", user=user)

# APIS DO DASHBOARD - TODAS PROTEGIDAS
@app.route("/api/dados_mercado")
@login_required
def dados_mercado():
    """API para dados de mercado"""
    return jsonify(get_public_market_data())

@app.route("/api/saldo")
@login_required
def api_saldo():
    """API para saldo do usuário"""
    user = User.query.get(session['user_id'])
    
    if user.binance_api_key:
        client = get_user_binance_client()
        if client:
            try:
                account_info = client.get_account()
                usdt_balance = next((item for item in account_info['balances'] if item['asset'] == 'USDT'), None)
                return jsonify({'saldo': usdt_balance['free'] if usdt_balance else '0', 'tipo': 'real'})
            except Exception as e:
                print(f"Erro Binance API: {e}")
    
    return jsonify({'saldo': f"{user.saldo_simulado:.2f}", 'tipo': 'simulado'})

@app.route("/api/sugestao_ia", methods=["POST"])
@login_required
def sugestao_ia():
    """API para sugestões de IA"""
    user = User.query.get(session['user_id'])
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON inválidos'}), 400
            
        prompt = data.get('prompt', '').strip()
        contexto = data.get('contexto', 'oraculo')
        
        if not prompt:
            return jsonify({'erro': 'Prompt é obrigatório'}), 400
        
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
                print(f"Erro OpenAI: {e}")
                return jsonify({'erro': 'Erro na API OpenAI. Verifique sua chave.'}), 500
        
        # Respostas simuladas por contexto
        respostas_contexto = {
            'oraculo': [
                "🔮 **VISÃO ORÁCULO** ✨\n\n🌟 **PREVISÃO MÍSTICA:**\nAs energias cósmicas revelam turbulência no éter digital! O BTC navega entre dimensões paralelas.\n\n⚡ **TRÊS CENÁRIOS REVELADOS:**\n• **🚀 ASCENSÃO:** Rompimento da barreira etérea → +7.3%\n• **⚖️ EQUILÍBRIO:** Dança entre portais dimensionais\n• **📉 PURIFICAÇÃO:** Teste das forças anciãs → -4.8%\n\n🎯 **ENTRADA SAGRADA:** Aguardar o alinhamento dos cristais\n🛡️ **PROTEÇÃO MÁGICA:** Escudo em 3.2% abaixo\n⏰ **CICLO TEMPORAL:** 4-8 horas terrestres\n\n✨ **CONFIANÇA ORÁCULO:** 79% das visões se alinham",
                "🔮 **MENSAGEM DO ORÁCULO** 🌟\n\n✨ Os ventos cósmicos sussurram mudanças... O RSI dança entre 42-58, zona de transição espiritual!\n\n🔥 **RITUAIS RECOMENDADOS:**\n• **MEDITAÇÃO:** Aguardar sinais mais claros\n• **PROTEÇÃO:** Stop em território sagrado\n• **MANIFESTAÇÃO:** Alvo nas constelações superiores\n\n🌙 **FASE LUNAR:** Crescente de oportunidades\n⭐ **ENERGIA DOMINANTE:** Paciência e precisão"
            ],
            'cosmo': [
                "🌌 **TRANSMISSÃO CÓSMICA** 🪐\n\n🔭 **ANÁLISE INTER-DIMENSIONAL:**\nObservando através do telescópio universal, veio perturbações no campo gravitacional financeiro.\n\n🌍 **FATORES PLANETÁRIOS:**\n• 🏛️ Saturno (Políticas) em quadratura\n• 💫 Júpiter (Liquidez) em retrogradação\n• ⚡ Marte (Volatilidade) ascendente\n\n🛸 **NAVEGAÇÃO:** BTC surfando ondas entre $94K-$97K\n⭐ **PRÓXIMO PORTAL:** 72 horas terrestres",
                "🌌 **CLARINHA COSMO ONLINE** 🛸\n\n🪐 Detectando anomalias no espaço-tempo financeiro...\n\n🌟 **STATUS QUADRANTES:**\n• Alpha (Ásia): Neutro 🟡\n• Beta (Europa): Pressão 🔴\n• Gamma (América): Acumulação 🟢\n\n🚀 **RECOMENDAÇÃO:** Órbita baixa até cessarem as tempestades solares"
            ],
            'inteligencia': [
                "🧠 **ANÁLISE QUÂNTICA** 💡\n\n📊 **PROCESSAMENTO COMPLETO:**\n```\nDADOS: 847,293 pontos\nPADRÕES: 23 fractais ativos\nCORRELAÇÕES: S&P500(0.73), DXY(0.81)\n```\n\n🎯 **MÉTRICAS:**\n• Probabilidade: 67.8% (6h)\n• Volatilidade: 31.2%\n• Volume: +18.7%\n• RSI: 54.3\n\n🔬 **RECOMENDAÇÃO:**\n• Posição: 3.2% capital\n• Entrada: $95,240\n• Stop: -2.9%\n• Target: +5.1%\n\n⚡ **CONFIANÇA:** 81.4%"
            ]
        }
        
        import random
        return jsonify({'resposta': random.choice(respostas_contexto.get(contexto, respostas_contexto['oraculo']))})
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route("/api/executar_operacao", methods=["POST"])
@login_required
def executar_operacao():
    """API para execução de operações"""
    user = User.query.get(session['user_id'])
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON inválidos'}), 400
            
        tipo = data.get('tipo')
        quantidade = float(data.get('quantidade', 0.001))
        
        if tipo not in ['comprar', 'vender']:
            return jsonify({'erro': 'Tipo de operação inválido'}), 400
            
        if quantidade <= 0:
            return jsonify({'erro': 'Quantidade deve ser maior que zero'}), 400
        
        # Tentar operação real primeiro
        if user.binance_api_key:
            client = get_user_binance_client()
            if client:
                try:
                    if tipo == 'comprar':
                        order = client.order_market_buy(symbol='BTCUSDT', quantity=quantidade)
                    else:
                        order = client.order_market_sell(symbol='BTCUSDT', quantity=quantidade)
                    
                    return jsonify({
                        'mensagem': f'✅ {tipo.capitalize()} executada com sucesso!', 
                        'detalhes': order,
                        'tipo': 'real'
                    })
                except Exception as e:
                    print(f"Erro Binance: {e}")
                    # Fallback para simulação
        
        # Operação simulada
        market_data = get_public_market_data()
        preco_atual = market_data['preco']
        valor_operacao = preco_atual * quantidade
        
        if tipo == 'comprar':
            if user.saldo_simulado >= valor_operacao:
                user.saldo_simulado -= valor_operacao
                mensagem = f'🚀 Compra simulada! -{valor_operacao:.2f} USDT'
            else:
                return jsonify({'erro': 'Saldo insuficiente'}), 400
        else:  # vender
            user.saldo_simulado += valor_operacao
            mensagem = f'💰 Venda simulada! +{valor_operacao:.2f} USDT'
        
        db.session.commit()
        return jsonify({'mensagem': mensagem, 'tipo': 'simulado'})
        
    except ValueError:
        return jsonify({'erro': 'Quantidade inválida'}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# TRATAMENTO DE ERROS
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_default_users()  # Criar usuários padrão
        print("\n🚀 CLARAVERSE INICIADO!")
        print("=" * 50)
        print("👤 USUÁRIOS DISPONÍVEIS:")
        print("• admin    | senha: Bubi2025   | Saldo: $15,000")
        print("• Clara    | senha: Verse      | Saldo: $25,000")
        print("• Soma     | senha: infinite   | Saldo: $50,000")
        print("=" * 50)
    
    app.run(debug=True, host="0.0.0.0", port=5000)