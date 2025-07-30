// static/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    // Função para rolar até um bloco ao clicar no menu
    document.querySelectorAll('.menu-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = btn.getAttribute('onclick').split("'")[1];
            const el = document.getElementById(id);
            if (el) el.scrollIntoView({ behavior: 'smooth' });
        });
    });

    // Função centralizada para disparar ordens
    window.confirmarOrdem = function(tipo) {
        if (!confirm("Confirma a ordem de " + (tipo === 'compra' ? "COMPRA" : "VENDA") + "?")) return;
        window.executarOrdem(tipo);
    };

    window.executarOrdem = function(tipo) {
        let quantidade = prompt("Informe a quantidade de BTC para operar:", "0.001");
        if (!quantidade || isNaN(parseFloat(quantidade))) return alert("Quantidade inválida!");
        axios.post('/executar_ordem', {
            tipo_ordem: tipo,
            simbolo: 'BTCUSDT',
            quantidade: quantidade
        })
        .then(resp => {
            document.getElementById('mensagem-ordem').innerHTML = "<b>" + resp.data.mensagem + "</b>";
            adicionarHistorico(resp.data);
        })
        .catch(err => {
            let msg = err.response && err.response.data && err.response.data.mensagem ? err.response.data.mensagem : "Erro na ordem.";
            document.getElementById('mensagem-ordem').innerHTML = "<span class='error'>" + msg + "</span>";
        });
    };

    window.obterSugestaoGPT = function() {
        document.getElementById('gpt-sugestao').innerHTML = "Consultando IA...";
        axios.post('/sugestao_gpt', { prompt: "Análise para operação BTCUSDT agora." })
            .then(resp => {
                document.getElementById('gpt-sugestao').innerHTML = "<b>Sugestão IA:</b><br>" + resp.data.sugestao;
            })
            .catch(err => {
                let msg = err.response && err.response.data && err.response.data.erro ? err.response.data.erro : "Erro na IA.";
                document.getElementById('gpt-sugestao').innerHTML = "<span class='error'>" + msg + "</span>";
            });
    };

    function adicionarHistorico(dados) {
        if (!dados || !dados.mensagem) return;
        const list = document.getElementById('historico-list');
        if (!list) return;
        const li = document.createElement('li');
        li.textContent = `${new Date().toLocaleTimeString()} - ${dados.mensagem}`;
        list.prepend(li);
    }

    // Se quiser buscar histórico do backend ao carregar:
    // axios.get('/historico_ordens').then(resp => { ... });

    // Exemplo para botão automático:
    window.executarOrdemAutomatico = function() {
        if (!confirm("Ativar modo automático de operações com IA Clarinha?")) return;
        axios.post('/executar_ordem', {
            tipo_ordem: 'automatico',
            simbolo: 'BTCUSDT'
        })
        .then(resp => {
            document.getElementById('mensagem-ordem').innerHTML = "<b>" + resp.data.mensagem + "</b>";
            adicionarHistorico(resp.data);
        })
        .catch(err => {
            let msg = err.response && err.response.data && err.response.data.mensagem ? err.response.data.mensagem : "Erro no automático.";
            document.getElementById('mensagem-ordem').innerHTML = "<span class='error'>" + msg + "</span>";
        });
    };
});
