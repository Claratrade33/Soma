# app.py (corrigido, completo, com relatório e integração aprimorada)
import os
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from clarinha_ia import ClarinhaIA

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'claraverse_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///claraverse.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Modelo de usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

# Modelo de operação
class Operacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    entrada = db.Column(db.String(50))
    alvo = db.Column(db.String(50))
    stop = db.Column(db.String(50))
    confianca = db.Column(db.String(50))
    sugestao = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# Decorador de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rota inicial
@app.route('/')
def index():
    return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('painel_operacao'))
        flash('Credenciais inválidas')
    return render_template('login.html')

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        novo_usuario = User(username=username, email=email, password=password)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Conta criada com sucesso! Faça login agora.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Painel de operação aprimorado com proteção, integração com IA e relatório
@app.route('/painel_operacao')
@login_required
def painel_operacao():
    ia = ClarinhaIA(os.getenv("OPENAI_API_KEY"))
    sugestao = ia.gerar_sugestao()

    # Salvando a operação gerada no relatório
    nova_operacao = Operacao(
        usuario_id=session['user_id'],
        entrada=sugestao.get("entrada"),
        alvo=sugestao.get("alvo"),
        stop=sugestao.get("stop"),
        confianca=sugestao.get("confianca"),
        sugestao=sugestao.get("sugestao")
    )
    db.session.add(nova_operacao)
    db.session.commit()

    # Obtendo operações anteriores para relatório
    operacoes = Operacao.query.filter_by(usuario_id=session['user_id']).order_by(Operacao.timestamp.desc()).all()

    return render_template('painel_operacao.html', sugestao=sugestao, operacoes=operacoes)

# Rota para relatório detalhado
def gerar_relatorio(usuario_id):
    operacoes = Operacao.query.filter_by(usuario_id=usuario_id).order_by(Operacao.timestamp.desc()).all()
    return operacoes

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)