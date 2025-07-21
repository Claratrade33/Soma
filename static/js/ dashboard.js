function mostrarMensagem(tipo, texto) {
    const divMensagem = document.getElementById('mensagem');
    divMensagem.className = `mensagem ${tipo}`; // Adiciona a classe de estilo
    divMensagem.innerText = texto; // Define o texto da mensagem
    divMensagem.style.display = 'block'; // Exibe a mensagem

    // Oculta a mensagem após 5 segundos
    setTimeout(() => {
        divMensagem.style.display = 'none';
    }, 5000);
}

async function executarAcao(acao) {
    try {
        const resposta = await fetch('/executar_acao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ acao: acao })
        });
        const resultado = await resposta.json();
        if (resultado.status) {
            mostrarMensagem('success', resultado.status);
        } else {
            mostrarMensagem('error', resultado.erro);
        }

        if (resultado.status && (resultado.status.includes('+') || resultado.status.includes('-'))) {
            location.reload();
        }
    } catch (error) {
        mostrarMensagem('error', 'Erro ao executar ação: ' + error);
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
            mostrarMensagem('success', 'Sugestão obtida com sucesso!');
        } else {
            mostrarMensagem('error', json.erro || "Erro inesperado.");
        }
    } catch (error) {
        divResposta.innerText = "Erro ao consultar a IA: " + error;
        mostrarMensagem('error', "Erro ao consultar a IA: " + error);
    }
}

async function carregarChavesAPI() {
    try {
        const resposta = await fetch('/obter_dados_binance'); // Ajuste a URL para a rota correta
        const json = await resposta.json();
        document.getElementById('openai-key').innerText = json.openai_key || 'Chave não disponível';
        document.getElementById('binance-key').innerText = json.binance_key || 'Chave não disponível';
        document.getElementById('binance-secret').innerText = json.binance_secret || 'Chave não disponível';
    } catch (error) {
        console.error('Erro ao carregar chaves:', error);
        mostrarMensagem('error', 'Erro ao carregar chaves: ' + error);
    }
}

// Chama a função para carregar as chaves assim que a página é carregada
window.onload = carregarChavesAPI;