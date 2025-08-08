from flask import Blueprint, render_template, request, redirect
from operacoes_automatico.leitura_mercado import obter_dados_mercado
from operacoes_automatico.inteligencia import executar_estrategia

# Define o blueprint sem um template_folder específico.
# Usaremos o padrão de resolução de templates do Flask, que busca em `templates/`.
operacoes_automatico_bp = Blueprint('operacoes_automatico', __name__)

@operacoes_automatico_bp.route('/painel_automatico')
def painel_automatico():
    labels, dados = obter_dados_mercado('BTCUSDT')
    estrategia = "Infinity Strike V2"
    ultima_acao = "Compra em suporte"
    status = "Ativa"
    resultado = "+2.8%"

    # Renderiza o template existente em templates/operacoes.
    return render_template(
        'operacoes/painel_automatico.html',
        labels=labels,
        dados=dados,
        estrategia=estrategia,
        ultima_acao=ultima_acao,
        status=status,
        resultado=resultado,
    )

@operacoes_automatico_bp.route('/operacoes_automatico/ativar', methods=['POST'])
def ativar_estrategia():
    executar_estrategia()
    return redirect('/painel_automatico')
