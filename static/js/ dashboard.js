// static/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
  // TradingView
  new TradingView.widget({
      "container_id": "tv_chart",
      "width": "100%",
      "height": 400,
      "symbol": "BINANCE:BTCUSDT",
      "interval": "30",
      "timezone": "America/Sao_Paulo",
      "theme": "dark",
      "style": "1",
      "locale": "br",
      "toolbar_bg": "#222",
      "hide_side_toolbar": false,
      "allow_symbol_change": false,
      "save_image": false
  });

  atualizarHistorico();
});

function confirmarOrdem(tipo) {
    const quantidade = prompt("Informe a quantidade de BTC para " + (tipo === 'compra' ? 'comprar' : 'vender') + ":", "0.001");
    if (!quantidade || isNaN(parseFloat(quantidade))) {
        alert("Quantidade inválida!");
        return;
    }
    if (!confirm(`Tem certeza que deseja ${tipo === 'compra' ? 'COMPRAR' : 'VENDER'} ${quantidade} BTC agora?`)) {
        return;
    }
    executarOrdem(tipo, quantidade);
}

function executarOrdem(tipo, quantidade) {
    axios.post('/executar_ordem', {
        tipo_ordem: tipo,
        simbolo: 'BTCUSDT',
        quantidade: quantidade
    })
    .then(resp => {
        document.getElementById('mensagem-ordem').innerHTML = "<b>" + resp.data.mensagem + "</b>";
        salvarHistorico(tipo, quantidade, resp.data.mensagem);
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

// Histórico local (pode adaptar pra backend depois)
function salvarHistorico(tipo, quantidade, mensagem) {
    let historico = JSON.parse(localStorage.getItem("historico_operacoes") || "[]");
    historico.unshift({
        data: new Date().toLocaleString(),
        tipo,
        quantidade,
        mensagem
    });
    if (historico.length > 10) historico = historico.slice(0, 10);
    localStorage.setItem("historico_operacoes", JSON.stringify(historico));
    atualizarHistorico();
}

function atualizarHistorico() {
    let historico = JSON.parse(localStorage.getItem("historico_operacoes") || "[]");
    const box = document.getElementById('historico');
    if (!box) return;
    if (historico.length === 0) {
        box.innerHTML = "<span>Nenhuma ordem executada ainda.</span>";
        return;
    }
    box.innerHTML = historico.map(h =>
        `<div class="hist-card">
            <b>${h.tipo.toUpperCase()}</b> | <span>${h.quantidade} BTC</span> | <small>${h.data}</small>
            <br><span class="msg">${h.mensagem}</span>
        </div>`
    ).join('');
}

let automatico = false;
function toggleAutomatico() {
    automatico = !automatico;
    if (automatico) {
        alert("Modo automático ativado! A cada 30s a IA dará uma sugestão e executará uma ordem (DEMO).");
        autoLoop();
    } else {
        alert("Modo automático desativado.");
    }
}

function autoLoop() {
    if (!automatico) return;
    obterSugestaoGPT();
    // Exemplo: executa ordem demo de compra de 0.001
    salvarHistorico("auto", "0.001", "Ordem automática simulada");
    setTimeout(autoLoop, 30000); // 30s
}
