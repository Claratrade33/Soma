document.addEventListener('DOMContentLoaded', () => {
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

      corpo.appendChild(tr);
    }
  }

