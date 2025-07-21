async function executarAcao(acao) {
    try {
        const resposta = await fetch('/executar_acao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ acao: acao })
        });
        const resultado = await resposta.json();
        alert(resultado.status || resultado.erro);
        if (resultado.status && (resultado.status.includes('+') || resultado.status.includes('-'))) {
            location.reload();
        }
    } catch (error) {
        alert('Erro ao executar ação: ' + error);
    }
}

async function obterSugestaoIA() {
    const divResposta = document.getElementById('resposta-ia');
    divResposta.innerHTML = "🔮 Clarinha está analisando o mercado...";
    try {
        const resposta = await fetch('/obter_sugestao_ia', { method: 'POST' });
        const json = await resposta.json();
        if (json.sugestao) {
            divResposta.innerHTML = `💡 <pre>${json.sugestao}</pre>`;
        } else {
            divResposta.innerText = json.erro || "Erro inesperado.";
        }
    } catch (error) {
        divResposta.innerText = "Erro ao consultar a IA: " + error;
    }
}

async function carregarChavesAPI() {
    try {
        const resposta = await fetch('/painel'); // Adapte a URL conforme necessário
        const json = await resposta.json();
        document.getElementById('openai-key').innerText = json.openai_key || 'Chave não disponível';
        document.getElementById('binance-key').innerText = json.binance_key || 'Chave não disponível';
        document.getElementById('binance-secret').innerText = json.binance_secret || 'Chave não disponível';
    } catch (error) {
        console.error('Erro ao carregar chaves:', error);
    }
}

// Chama a função para carregar as chaves assim que a página é carregada
window.onload = carregarChavesAPI;