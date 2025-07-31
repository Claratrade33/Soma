document.addEventListener('DOMContentLoaded', () => {
  // Histórico local (simulação visual)
  let historico = [];

  function renderHistorico() {
    const ordensList = document.getElementById('ordens-list');
    if (!ordensList) return;
    ordensList.innerHTML = "";
    for (let o of historico) {
      let li = document.createElement('li');
      li.innerHTML = `<b>${o.tipo}</b> ${o.ativo} - ${o.valor} @ ${o.preco} <span style="color:#aaa">${o.hora}</span>`;
      ordensList.appendChild(li);
    }
  }

  window.confirmarOrdem = function(tipo) {
    let msg = "Tem certeza que deseja executar essa ordem?";
    if (tipo === "buy") msg = "Confirmar compra?";
    if (tipo === "sell") msg = "Confirmar venda?";
    if (tipo === "suggest") msg = "Pedir sugestão para a IA?";
    if (tipo === "auto") msg = "Ativar modo automático?";
    if (confirm(msg)) {
      let valor = document.getElementById("qtd_input")?.value || "0.001";
      historico.unshift({
        tipo: tipo === "buy" ? "Compra" :
              tipo === "sell" ? "Venda" :
              tipo === "suggest" ? "Sugestão IA" : "Automático",
        ativo: "BTCUSDT",
        valor: valor,
        preco: "ao vivo",
        hora: new Date().toLocaleTimeString().slice(0,5)
      });
      renderHistorico();
      alert("Ordem executada!");
      // Para ordens reais, faça requisição Ajax para /executar_ordem
    }
  };

  renderHistorico();
});
