async function executarAcao(acao) {
    const botao = document.querySelector(`button[onclick*="${acao}"]`);
    if (botao) botao.disabled = true;

    try {
        const resposta = await fetch('/executar_acao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ acao: acao })
        });

        const resultado = await resposta.json();
        alert(resultado.status || resultado.erro);
        if (resultado.status && resultado.status.includes('+') || resultado.status.includes('-')) {
            location.reload();
        }
    } catch (erro) {
        alert('Erro: ' + erro);
    } finally {
        if (botao) botao.disabled = false;
    }
}

async function obterSugestaoIA() {
    const div = document.getElementById('resposta-ia');
    div.innerText = '🔮 Consultando Clarinha...';

    try {
        const resposta = await fetch('/obter_sugestao_ia', {
            method: 'POST'
        });
        const json = await resposta.json();
        if (json.sugestao) {
            div.innerText = json.sugestao;
        } else {
            div.innerText = json.erro || 'Erro desconhecido.';
        }
    } catch (erro) {
        div.innerText = 'Erro ao obter sugestão: ' + erro;
    }
}