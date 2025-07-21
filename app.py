from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from models import User
from binance.client import Client as BinanceClient
import openai
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

# Variáveis de ambiente para chaves de API
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Inicializando os clientes
binance_client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)
openai.api_key = OPENAI_API_KEY

@app.route("/")
def index():
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

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/obter_preco", methods=["GET"])
def obter_preco():
    try:
        ticker = binance_client.get_symbol_ticker(symbol="BTCUSDT")
        return jsonify({'preco': ticker['price']})
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