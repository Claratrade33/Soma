// static/dashboard.js

function executarOrdem(tipo) {
    const quantidade = prompt("Informe a quantidade de BTC para " + (tipo === 'compra' ? 'comprar' : 'vender') + ":", "0.001");
    if (!quantidade || isNaN(parseFloat(quantidade))) return alert("Quantidade inválida!");
    axios.post('/executar_ordem', {
        tipo_ordem: tipo,
        simbolo: 'BTCUSDT',
        quantidade: quantidade
    })
    .then(resp => {
        document.getElementById('mensagem-ordem').innerHTML = "<b>" + resp.data.mensagem + "</b>";
    })
    .catch(err => {
        let msg = err.response && err.response.data && err.response.data.mensagem ? err.response.data.mensagem : "Erro na ordem.";
        document.getElementById('mensagem-ordem').innerHTML = "<span class='error'>" + msg + "</span>";
    });
}

function obterSugestaoGPT() {
    document.getElementById('gpt-sugestao').innerHTML = "Consultando IA...";
    axios.post('/sugestao_gpt', { prompt: "Análise para operação BTCUSDT agora." })
        .then(resp => {
            document.getElementById('gpt-sugestao').innerHTML = "<b>Sugestão IA:</b><br>" + resp.data.sugestao;
        })
        .catch(err => {
            let msg = err.response && err.response.data && err.response.data.erro ? err.response.data.erro : "Erro na IA.";
            document.getElementById('gpt-sugestao').innerHTML = "<span class='error'>" + msg + "</span>";
        });
}
