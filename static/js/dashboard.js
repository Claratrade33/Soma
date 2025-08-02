document.addEventListener('DOMContentLoaded', () => {
  // Histórico local (simulação visual)
  let historico = [];

  async function atualizarHistorico() {
    try {
      const resp = await fetch("/historico");
      if (resp.ok) {
        historico = await resp.json();
        renderHistorico();
      }
    } catch (e) {
      console.error("Erro ao atualizar histórico", e);
    }
  }

  function renderHistorico() {
    const corpo = document.querySelector('#ordens-table tbody');
    if (!corpo) return;
    corpo.innerHTML = "";
    for (let o of historico) {
      const tr = document.createElement('tr');
      const tipoLower = (o.tipo || '').toLowerCase();
      let tipoClass = '';
      if (tipoLower.includes('compra')) tipoClass = 'compra';
      if (tipoLower.includes('venda')) tipoClass = 'venda';
      tr.innerHTML = `
        <td class="tipo-${tipoClass}">${o.tipo}</td>
        <td>${o.ativo}</td>
        <td>${o.valor}</td>
        <td>${o.preco}</td>
        <td>${o.hora}</td>`;
      corpo.appendChild(tr);
    }
  }

  window.confirmarOrdem = async function(tipo) {
    let msg = "Tem certeza que deseja executar essa ordem?";
    if (tipo === "buy") msg = "Confirmar compra?";
    if (tipo === "sell") msg = "Confirmar venda?";
    if (tipo === "suggest") msg = "Pedir sugestão para a IA?";
    if (tipo === "auto") msg = "Ativar modo automático?";
    if (confirm(msg)) {
      let valor = document.getElementById("qtd_input")?.value || "0.001";
      if (tipo === "buy" || tipo === "sell") {
        const form = new URLSearchParams();
        form.append("tipo", tipo === "buy" ? "compra" : "venda");
        form.append("quantidade", valor);
        try {
          const resp = await fetch("/executar_ordem", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: form.toString()
          });
          if (resp.ok) {
            alert("Ordem executada!");
            await atualizarHistorico();
          } else {
            alert("Erro ao executar ordem");
          }
        } catch (e) {
          console.error("Erro ao executar ordem", e);
        }
      } else {
        historico.unshift({
          tipo: tipo === "suggest" ? "Sugestão IA" : "Automático",
          ativo: "BTCUSDT",
          valor: valor,
          preco: "ao vivo",
          hora: new Date().toLocaleTimeString().slice(0,5)
        });
        renderHistorico();
      }
    }
  };

  atualizarHistorico();
});
