from flask import render_template
from . import bp


@bp.route('/')
def lista_tokens():
    return render_template('tokens/lista_tokens.html')


@bp.route('/gerar')
def gerar_token():
    return render_template('tokens/gerar_token.html')
