from flask import render_template

from . import bp


@bp.route('/')
def index():
    """Render the operations panel."""
    return render_template('operacoes/painel_operacao.html')
