document.addEventListener('DOMContentLoaded', () => {
  const botaoAuto = document.getElementById('btn-auto');
  const statusAuto = document.getElementById('status-auto');

  let modoAtivo = false;
  let intervaloIA;

  const atualizarIA = async () => {
    try {
      const res = await fetch('/sinal_ia');
      const dados = await res.json();
      document.getElementById('sinal-ia').innerHTML = `
        📣 IA Clarinha - Sinal ao vivo:<br>
        ${JSON.stringify(dados)}
      `;

      if (modoAtivo && dados.sinal !== "Erro") {
        await fetch('/executar_ordem', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(dados)
        });
      }
    } catch (e) {
      console.error('Erro na IA:', e);
    }
  };

  if (botaoAuto) {
    botaoAuto.addEventListener('click', () => {
      modoAtivo = !modoAtivo;

      if (modoAtivo) {
        statusAuto.innerText = 'IA Ativa 🔁';
        atualizarIA();
        intervaloIA = setInterval(atualizarIA, 15000); // a cada 15 segundos
      } else {
        statusAuto.innerText = 'IA Desativada ⛔';
        clearInterval(intervaloIA);
      }
    });
  }

  // Botões manuais (Entrada / Stop / Alvo)
  document.getElementById('btn-entrada')?.addEventListener('click', () => {
    fetch('/executar_ordem', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ sinal: 'BUY' })
    });
  });

  document.getElementById('btn-stop')?.addEventListener('click', () => {
    fetch('/executar_ordem', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ sinal: 'STOP' })
    });
  });

  document.getElementById('btn-alvo')?.addEventListener('click', () => {
    fetch('/executar_ordem', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ sinal: 'SELL' })
    });
  });
});

