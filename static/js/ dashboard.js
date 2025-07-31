document.addEventListener('DOMContentLoaded', () => {
  const ordensList = document.getElementById('ordens-list');
  const qtdInput = document.getElementById('qtd_input') || { value: "0.001" };
  let historico = [];

  // Função para inserir nova ordem no histórico
  window.confirmarOrdem = function(tipo) {
    let msg = "Tem certeza que deseja executar essa ordem?";
    if (tipo === "buy") msg = "Confirmar compra?";
    if (tipo === "sell") msg = "Confirmar venda?";
    if (tipo === "ia") msg = "Pedir sugestão para a IA?";
    if (tipo === "auto") msg = "Ativar modo automático?";
    if (confirm(msg)) {
      historico.unshift({
        tipo: tipo === "buy" ? "Compra" : tipo === "sell" ? "Venda" : (tipo === "ia" ? "Sugestão IA" : "Automático"),
        ativo: "BTCUSDT",
        valor: qtdInput.value || "0.001",
        preco: "ao vivo",
        hora: new Date().toLocaleTimeString().slice(0,5)
      });
      renderHistorico();
      alert("Ordem executada!");
    }
  }

  function renderHistorico() {
    if (!ordensList) return;
    ordensList.innerHTML = "";
    for (let o of historico) {
      let li = document.createElement('li');
      li.innerHTML = `<b>${o.tipo}</b> ${o.ativo} - ${o.valor} @ ${o.preco} <span style="color:#aaa">${o.hora}</span>`;
      ordensList.appendChild(li);
    }
  }

  renderHistorico();
});
