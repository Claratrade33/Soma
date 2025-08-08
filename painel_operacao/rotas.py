from flask import Blueprint, render_template

bp = Blueprint('painel_operacao', __name__)

@bp.route("/")
def index():
    return render_template("operacoes/painel_operacao.html")
