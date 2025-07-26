from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from binance.client import Client
from clarinha_ia import ClarinhaIA
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_claraverse')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=6)

db = SQLAlchemy(app)
ia_clarinha = ClarinhaIA()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    binance_key = db.Column(db.String(255))
    binance_secret = db.Column(db.String(255))
    openai_key = db.Column(db.String(255))

@app.before_request
def make_session_permanent():
    session.permanent = True

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash('Email já registrado.')
        else:
            novo = User(username=username, email=email, password=password)
            db.session.add(novo)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/painel_operacao')
@login_required
def painel_operacao():
    user = User.query.get(session['user_id'])
    if not user or not user.binance_key or not user.binance_secret:
        return redirect('/configurar')
    try:
        client = Client(user.binance_key, user.binance_secret)
        saldo = client.get_asset_balance(asset='USDT')
        saldo_real = saldo['free']
    except Exception:
        saldo_real = "Erro"

    sugestao = ia_clarinha.gerar_sugestao(modo='real', chave=user.openai_key)

    return render_template('painel_operacao.html', saldo=saldo_real, sugestao=sugestao)

@app.route('/configurar', methods=['GET', 'POST'])
@login_required
def configurar():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.binance_key = request.form['binance_key']
        user.binance_secret = request.form['binance_secret']
        user.openai_key = request.form['openai_key']
        db.session.commit()
        return redirect(url_for('painel_operacao'))
    return render_template('configurar.html')

@app.route('/executar_ordem', methods=['POST'])
@login_required
def executar_ordem():
    user = User.query.get(session['user_id'])
    client = Client(user.binance_key, user.binance_secret)
    simbolo = request.json['simbolo']
    lado = request.json['lado']
    quantidade = float(request.json['quantidade'])

    try:
        ordem = client.create_order(
            symbol=simbolo,
            side=lado,
            type='MARKET',
            quantity=quantidade
        )
        return jsonify({'status': 'Ordem executada', 'ordem': ordem})
    except Exception as e:
        return jsonify({'status': 'Erro', 'mensagem': str(e)})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)