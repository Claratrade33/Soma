from flask import render_template
from . import bp


@bp.route('/')
def painel():
    return render_template('conectores/painel_conectores.html')


@bp.route('/configurar')
def configurar_api():
    return render_template('conectores/configurar_api.html')
