from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
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

# DECORADOR DE PROTEÇÃO DE ROTAS
def login_required(f):
    """Decorador para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página!', 'warning')
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
        },
        {
            'username': 'Clara',
            'email': 'clara@claraverse.com',
            'password': 'Verse',
        },
        {
            'username': 'Soma',
            'email': 'soma@claraverse.com',
            'password': 'infinite',
        }
    ]
    
    for user_data in default_users:
        if not User.query.filter_by(username=user_data['username']).first():
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password'])
            )
            db.session.add(new_user)
    
    db.session.commit()

# ROTAS PRINCIPAIS
@app.route("/")
def index():
    """Rota principal"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Rota de registro"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(username=username).first():
            flash('Username já existe! Escolha outro.', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado! Use outro email.', 'error')
            return render_template("register.html")
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('🎉 Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Rota de login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        login_field = request.form.get('username', '').strip()  # Pode ser username ou email
        password = request.form.get('password', '')
        
        user = User.query.filter(
            (User.username == login_field) | (User.email == login_field)
        ).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Bem-vindo(a), {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login ou senha incorretos!', 'error')
    
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard do usuário"""
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    """Rota de logout"""
    session.clear()
    flash('Você saiu com sucesso!', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_default_users()  # Criar usuários padrão
    app.run(debug=True, host="0.0.0.0", port=5000)