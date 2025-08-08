from flask import render_template
from . import bp


@bp.route('/painel')
def painel_operacoes():
    """Display the operations panel."""
    return render_template('operacoes/painel_operacao.html')
