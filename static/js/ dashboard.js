function mostrarMensagem(tipo, texto) {
    const divMensagem = document.getElementById('mensagem');
    if (divMensagem) {
        divMensagem.className = `mensagem ${tipo}`; // Adiciona a classe de estilo
        divMensagem.innerText = texto; // Define o texto da mensagem
        divMensagem.style.display = 'block'; // Exibe a mensagem
        divMensagem.style.opacity = 0; // Começa invisível

        // Animação de desvanecimento
        setTimeout(() => {
            divMensagem.style.opacity = 1; // Torna visível
        }, 10); // Pequeno atraso para garantir que o display esteja 'block'

        // Oculta a mensagem após 5 segundos
        setTimeout(() => {
            divMensagem.style.opacity = 0; // Começa a desvanecer
            setTimeout(() => {
                divMensagem.style.display = 'none'; // Esconde completamente após a animação
            }, 500); // Tempo de espera para o desvanecimento
        }, 5000); // Tempo total de exibição
    } else {
        console.error('Elemento de mensagem não encontrado.');
    }
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
            mostrarMensagem('error', resultado.erro || "Erro inesperado.");
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
    if (divResposta) {
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
    } else {
        console.error('Elemento de resposta não encontrado.');
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
document.addEventListener('DOMContentLoaded', carregarChavesAPI);