from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, ApiKeysForm
from models import User
from binance.client import Client as BinanceClient
import openai
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

@app.route("/")
def index():
    # Aqui você pode buscar dados públicos, como o preço do BTC
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Aqui você deve adicionar a lógica de autenticação
        return redirect(url_for('dashboard'))
    return render_template("login.html", form=form)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = User.query.first()  # Aqui você deve buscar o usuário logado
    if request.method == "POST":
        # Lógica para salvar as chaves de API
        user.binance_api_key = request.form['binance_api_key']
        user.binance_api_secret = request.form['binance_api_secret']
        user.openai_api_key = request.form['openai_api_key']
        db.session.commit()
        flash('Chaves de API atualizadas com sucesso!')
    
    return render_template("dashboard.html", user=user)

@app.route("/obter_preco", methods=["GET"])
def obter_preco():
    # Retorna o preço do BTC usando dados públicos
    try:
        # Se não houver chaves, retorna dados públicos
        ticker = {'price': 'Dados públicos: preço do BTC aqui.'}
        return jsonify(ticker)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route("/obter_sugestao_ia", methods=["POST"])
def obter_sugestao_ia():
    prompt = request.json.get('prompt', 'Sugira uma ação de trading para o par BTC/USDT.')
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({'resposta': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)