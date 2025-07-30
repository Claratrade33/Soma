document.addEventListener('DOMContentLoaded', () => {
  const ordensList = document.getElementById('ordens-list');
  let historico = [];

  // Simula histórico ao carregar (remova depois para usar Ajax/BD)
  // historico = [
  //   { tipo: "Compra", ativo: "BTCUSDT", valor: "0.001", preco: "67600", hora: "10:12" },
  //   { tipo: "Venda", ativo: "BTCUSDT", valor: "0.001", preco: "67590", hora: "10:08" }
  // ];
  renderHistorico();

  // Função para inserir nova ordem
  window.confirmarOrdem = function(tipo) {
    let msg = "Tem certeza que deseja executar essa ordem?";
    if (tipo === "compra") msg = "Confirmar compra?";
    if (tipo === "venda") msg = "Confirmar venda?";
    if (tipo === "sugestao") msg = "Pedir sugestão para a IA?";
    if (tipo === "auto") msg = "Ativar modo automático?";
    if (!confirm(msg)) return false;

    if (tipo === "compra" || tipo === "venda") {
      const form = document.getElementById('form-ordem');
      const quantidade = form.querySelector('input[name="quantidade"]').value;
      if (!quantidade || isNaN(quantidade) || Number(quantidade) <= 0) {
        alert("Informe a quantidade para operar.");
        return false;
      }
      // POST para backend Flask
      fetch('/executar_ordem', {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `tipo=${tipo}&quantidade=${quantidade}&symbol=BTCUSDT`
      }).then(resp => resp.json()).then(dados => {
        historico.unshift({
          tipo: tipo === "compra" ? "Compra" : "Venda",
          ativo: "BTCUSDT",
          valor: quantidade,
          preco: (dados && dados.order && dados.order.fills && dados.order.fills[0]?.price) || '-',
          hora: new Date().toLocaleTimeString().slice(0,5)
        });
        renderHistorico();
        alert("Ordem enviada! Confira o status na Binance.");
      }).catch(e => {
        alert("Erro ao executar ordem: " + e);
      });
    } else {
      historico.unshift({
        tipo: tipo === "sugestao" ? "Sugestão IA" : "Automático",
        ativo: "BTCUSDT",
        valor: "-",
        preco: "-",
        hora: new Date().toLocaleTimeString().slice(0,5)
      });
      renderHistorico();
      alert("Função em breve.");
    }
    return false;
  }

  function renderHistorico() {
    ordensList.innerHTML = "";
    if (!historico.length) {
      ordensList.innerHTML = `<li style="opacity:.6">Nenhuma ordem registrada ainda.</li>`;
      return;
    }
    for (let o of historico) {
      let li = document.createElement('li');
      li.innerHTML = `<b>${o.tipo}</b> ${o.ativo} - ${o.valor} @ ${o.preco} <span style="color:#aaa">${o.hora}</span>`;
      ordensList.appendChild(li);
    }
  }
});