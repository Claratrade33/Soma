from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from binance.client import Client
from clarinha_ia import ClarinhaIA
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claraverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    binance_api_key = db.Column(db.String(300))
    binance_secret_key = db.Column(db.String(300))
    openai_api_key = db.Column(db.String(300))


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/painel_operacao')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/painel_operacao')
        return render_template('login.html', erro='Credenciais inválidas')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            return render_template('register.html', erro='Email já cadastrado.')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/painel_operacao')
def painel_operacao():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])

    saldo = "0.00"
    try:
        if user.binance_api_key and user.binance_secret_key:
            cliente = Client(user.binance_api_key, user.binance_secret_key)
            conta = cliente.get_asset_balance(asset='USDT')
            saldo = conta['free']
    except Exception:
        pass

    return render_template('painel_operacao.html', saldo=saldo)


@app.route('/configurar', methods=['GET', 'POST'])
def configurar():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.binance_api_key = request.form.get('binance_api_key')
        user.binance_secret_key = request.form.get('binance_secret_key')
        user.openai_api_key = request.form.get('openai_api_key')
        db.session.commit()
        return redirect('/painel_operacao')

    return render_template('configurar.html', user=user)


@app.route('/executar_ordem', methods=['POST'])
def executar_ordem():
    if 'user_id' not in session:
        return jsonify({'status': 'erro', 'mensagem': 'Não autenticado.'})

    user = User.query.get(session['user_id'])

    acao = request.json.get('acao')
    simbolo = 'BTCUSDT'
    quantidade = 0.001

    try:
        cliente = Client(user.binance_api_key, user.binance_secret_key)
        if acao == 'compra':
            ordem = cliente.order_market_buy(symbol=simbolo, quantity=quantidade)
        elif acao == 'venda':
            ordem = cliente.order_market_sell(symbol=simbolo, quantity=quantidade)
        else:
            return jsonify({'status': 'erro', 'mensagem': 'Ação inválida'})
        return jsonify({'status': 'sucesso', 'mensagem': 'Ordem executada com sucesso'})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)})


@app.route('/sugestao_ia')
def sugestao_ia():
    if 'user_id' not in session:
        return jsonify({'erro': 'Não autenticado'})

    user = User.query.get(session['user_id'])

    if not user.openai_api_key:
        return jsonify({'erro': 'Chave OpenAI não configurada'})

    try:
        clarinha = ClarinhaIA(user.openai_api_key)
        resposta = clarinha.analisar()
        return jsonify(resposta)
    except Exception as e:
        return jsonify({'erro': str(e)})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)