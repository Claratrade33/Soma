document.addEventListener('DOMContentLoaded', () => {
  // Histórico simulado só pra exibir UI (troque por Ajax depois)
  const ordensList = document.getElementById('ordens-list');
  let historico = [
    { tipo: "Compra", ativo: "BTCUSDT", valor: "0.001", preco: "67600", hora: "10:12" },
    { tipo: "Venda", ativo: "BTCUSDT", valor: "0.001", preco: "67590", hora: "10:08" }
  ];
  renderHistorico();

  // Função para inserir nova ordem no histórico
  window.confirmarOrdem = function(tipo) {
    let msg = "Tem certeza que deseja executar essa ordem?";
    if (tipo === "buy") msg = "Confirmar compra?";
    if (tipo === "sell") msg = "Confirmar venda?";
    if (tipo === "suggest") msg = "Pedir sugestão para a IA?";
    if (tipo === "auto") msg = "Ativar modo automático?";
    if (confirm(msg)) {
      // Simulação, depois chama endpoint Flask
      historico.unshift({
        tipo: tipo === "buy" ? "Compra" : tipo === "sell" ? "Venda" : (tipo === "suggest" ? "Sugestão IA" : "Automático"),
        ativo: "BTCUSDT",
        valor: "0.001",
        preco: "67700",
        hora: new Date().toLocaleTimeString().slice(0,5)
      });
      renderHistorico();
      alert("Ordem executada!");
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