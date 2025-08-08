# painel_operacao/rotas.py
from flask import render_template
from . import bp  # importa o blueprint criado em __init__.py

@bp.route("/")
def index():
    return render_template("operacoes/painel_operacao.html")
