from flask import render_template
from . import bp


@bp.route('/')
def painel():
    return render_template('configuracao/painel_configuracao.html')
