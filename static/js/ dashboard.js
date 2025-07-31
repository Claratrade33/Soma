document.addEventListener('DOMContentLoaded', () => {
  let historico = [];

  // ===== ATUALIZAR SALDO DA CARTEIRA =====
  function atualizarSaldo() {
    fetch('/api/saldo')
      .then(res => res.json())
      .then(data => {
        document.getElementById('saldo-btc').textContent = data.saldo_btc || "0";
        document.getElementById('saldo-usdt').textContent = data.saldo_usdt || "0";
      });
  }
  atualizarSaldo();

  // ===== ATUALIZAR DADOS DO ATIVO (PREÇO/RSI/VOLUME) =====
  function atualizarInfos() {
    fetch('/api/info_ativo?symbol=BTCUSDT')
      .then(res => res.json())
      .then(data => {
        document.getElementById('preco-ativo').textContent = data.preco || "-";
        document.getElementById('rsi-ativo').textContent = data.rsi || "-";
        document.getElementById('volume-ativo').textContent = data.volume || "-";
      });
  }
  atualizarInfos();
  setInterval(atualizarInfos, 10000);

  // ===== HISTÓRICO =====
  function renderHistorico() {
    const ordensList = document.getElementById('ordens-list');
    ordensList.innerHTML = "";
    for (let o of historico) {
      let li = document.createElement('li');
      li.innerHTML = `<b>${o.tipo}</b> ${o.ativo} - ${o.valor} @ ${o.preco} <span style="color:#aaa">${o.hora}</span>`;
      ordensList.appendChild(li);
    }
  }

  // ===== BOTÕES PRINCIPAIS =====
  window.confirmarOrdem = function(tipo) {
    let msg = "Tem certeza que deseja executar essa ordem?";
    let tipoApi = "";
    if (tipo === "buy") { msg = "Confirmar compra?"; tipoApi = "compra"; }
    if (tipo === "sell") { msg = "Confirmar venda?"; tipoApi = "venda"; }
    if (tipo === "suggest") { msg = "Pedir sugestão para a IA?"; tipoApi = "sugestao"; }
    if (tipo === "auto") { msg = "Ativar modo automático?"; tipoApi = "auto"; }

    if (tipoApi === "auto") {
      alert("Modo automático em breve! Aguarde atualização.");
      return;
    }
    if (tipoApi === "sugestao") {
      fetch('/api/sugestao_ia', { method: "POST" })
        .then(res => res.json())
        .then(data => {
          alert("Sugestão da IA:\n" + (data.sugestao || "Nada retornado"));
        });
      return;
    }

    const quantidade = document.getElementById('qtd_input').value || "";
    if (!quantidade || Number(quantidade) <= 0) {
      alert("Informe a quantidade para operar.");
      return;
    }
    const symbol = "BTCUSDT";
    if (!confirm(msg)) return;

    fetch('/executar_ordem', {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `tipo=${encodeURIComponent(tipoApi)}&quantidade=${encodeURIComponent(quantidade)}&symbol=${symbol}`
    })
    .then(res => res.json().catch(() => null))
    .then(data => {
      if (!data || data.status !== "ok") {
        alert("Erro ao executar ordem!\n" + (data && data.order ? data.order : ''));
        return;
      }
      const agora = new Date();
      historico.unshift({
        tipo: tipoApi === "compra" ? "Compra" : "Venda",
        ativo: symbol,
        valor: quantidade,
        preco: data.order && data.order.fills && data.order.fills[0] ? data.order.fills[0].price : "enviado",
        hora: agora.toLocaleTimeString().slice(0,5)
      });
      renderHistorico();
      atualizarSaldo();
      alert("Ordem executada!");
    })
    .catch(e => {
      alert("Erro ao executar ordem!\n" + e);
    });
  };

  renderHistorico();
});
