async function executarAcao(acao) {
    try {
        const resposta = await fetch('/executar_acao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ acao: acao })
        });
        const resultado = await resposta.json();
        alert(resultado.status || resultado.erro);
        if (resultado.status && resultado.status.includes('+')) {
            location.reload(); // Atualiza saldo após lucro
        }
    } catch (error) {
        alert('Erro ao executar ação: ' + error);
    }
}

async function obterSugestaoIA() {
    const divResposta = document.getElementById('resposta-ia');
    divResposta.innerText = "🔄 Consultando Clarinha...";
    try {
        const resposta = await fetch('/obter_sugestao_ia', {
            method: 'POST'
        });
        const resultado = await resposta.json();
        if (resultado.sugestao) {
            divResposta.innerText = resultado.sugestao;
        } else {
            divResposta.innerText = resultado.erro || 'Erro desconhecido.';
        }
    } catch (error) {
        divResposta.innerText = 'Erro: ' + error;
    }
}