document.addEventListener('DOMContentLoaded', () => {
    const respostaIa = document.getElementById('resposta-ia');
    const statusOperacao = document.getElementById('status-operacao');

    async function obterSugestaoIA() {
        try {
            const resposta = await fetch('/obter_sugestao_ia', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: 'Qual a melhor operação agora no par BTC/USDT?' })
            });

            const dados = await resposta.json();
            respostaIa.innerText = dados.resposta || dados.erro;
        } catch (erro) {
            respostaIa.innerText = 'Erro ao obter sugestão da IA.';
        }
    }

    async function executarAcao(acao) {
        try {
            const resposta = await fetch('/executar_acao', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ acao })
            });

            const dados = await resposta.json();
            statusOperacao.innerText = dados.status || dados.erro;
        } catch (erro) {
            statusOperacao.innerText = 'Erro ao executar ação.';
        }
    }

    document.getElementById('botao-entrada')?.addEventListener('click', () => executarAcao('entrada'));
    document.getElementById('botao-stop')?.addEventListener('click', () => executarAcao('stop'));
    document.getElementById('botao-alvo')?.addEventListener('click', () => executarAcao('alvo'));
    document.getElementById('botao-automatico')?.addEventListener('click', () => executarAcao('automatico'));
    document.getElementById('botao-executar')?.addEventListener('click', obterSugestaoIA);
});