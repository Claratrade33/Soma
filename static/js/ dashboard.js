// static/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
  const ordensList = document.getElementById('ordens-list');
  let historico = [];

  // Carregar histórico real via Ajax (Flask) ao carregar a página
  fetch('/historico_ordens')
    .then(res => res.json())
    .then(data => {
      if (Array.isArray(data)) {
        historico = data;
        renderHistorico();
      }
    });

  // Função global para confirmar e executar ordens reais
  window.confirmarOrdem = function(tipo) {
    let msg = "Tem certeza que deseja executar essa ordem?";
    if (tipo === "buy") msg = "Confirmar compra?";
    if (tipo === "sell") msg = "Confirmar venda?";
    if (tipo === "suggest") msg = "Pedir sugestão para a IA?";
    if (tipo === "auto") msg = "Ativar modo automático?";
    if (confirm(msg)) {
      // Chama endpoint Flask para executar ordem real
      fetch('/executar_ordem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tipo })
      })
      .then(res => res.json())
      .then(resp => {
        if (resp.status === "ok") {
          historico.unshift({
            tipo: resp.tipo || tipo,
            ativo: resp.ativo || "BTCUSDT",
            valor: resp.valor || resp.quantidade || "0.001",
            preco: resp.preco || resp.price || "-",
            hora: new Date().toLocaleTimeString().slice(0, 5)
          });
          renderHistorico();
          alert("Ordem executada!");
        } else {
          alert("Erro: " + (resp.erro || resp.message || "Erro ao executar ordem!"));
        }
      });
    }
  }

  function renderHistorico() {
    ordensList.innerHTML = "";
    for (let o of historico) {
      let li = document.createElement('li');
      li.innerHTML = `<b>${o.tipo}</b> ${o.ativo} - ${o.valor} @ ${o.preco} <span style="color:#aaa">${o.hora}</span>`;
      ordensList.appendChild(li);
    }
  }
});