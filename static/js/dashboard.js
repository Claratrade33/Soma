document.addEventListener('DOMContentLoaded', () => {
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

  async function executarCompraVenda(tipo, valor) {
    const form = new URLSearchParams();
    form.append("tipo", tipo);
    form.append("quantidade", valor);
    try {
      const resp = await fetch("/executar_ordem", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form.toString()
      });
      if (resp.ok) {
        alert("Ordem executada com sucesso!");
        await atualizarHistorico();
      } else {
        const msg = await resp.text();
        alert("Erro: " + msg);
      }
    } catch (e) {
      alert("Falha ao enviar ordem");
      console.error(e);
    }
  }

  async function pedirSugestaoIA(valor) {
    try {
      const resp = await fetch("/sugestao_ia?quantidade=" + valor);
      const data = await resp.json();
      if (data.tipo && data.status === "ok") {
        await executarCompraVenda(data.tipo, data.quantidade || valor);
      } else {
        alert("IA não retornou sugestão válida.");
      }
    } catch (e) {
      console.error("Erro ao consultar IA", e);
      alert("Erro ao pedir sugestão para a IA.");
    }
  }

  async function ativarAutomatico() {
    try {
      const resp = await fetch("/modo_automatico", { method: "POST" });
      const data = await resp.json();
      if (data.status === "ok") {
        alert("Modo automático ativado.");
      } else {
        alert("Erro ao ativar automático: " + (data.erro || "desconhecido"));
      }
    } catch (e) {
      console.error("Erro no modo automático", e);
      alert("Erro ao ativar automático.");
    }
  }

  window.confirmarOrdem = async function(tipo) {
    let valor = document.getElementById("qtd_input")?.value || "0.001";
    let msg = {
      buy: "Confirmar compra?",
      sell: "Confirmar venda?",
      suggest: "Pedir sugestão da IA e executar?",
      auto: "Deseja ativar o modo automático?"
    }[tipo] || "Executar ação?";
    
    if (!confirm(msg)) return;

    if (tipo === "buy" || tipo === "sell") {
      await executarCompraVenda(tipo === "buy" ? "compra" : "venda", valor);
    } else if (tipo === "suggest") {
      await pedirSugestaoIA(valor);
    } else if (tipo === "auto") {
      await ativarAutomatico();
    }

    await atualizarHistorico();
  };

  atualizarHistorico();
});