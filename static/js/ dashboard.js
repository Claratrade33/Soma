document.addEventListener('DOMContentLoaded', () => {
  const sinaisContainer = document.getElementById('sinais-container');
  const chartIcon = document.querySelector('img[src*="chart.svg"]');

  // Sinais simulados recebidos da Clarinha
  const sinais = [
    { id: 1, tipo: 'RSI', valor: 72, intensidade: 'forte' },
    { id: 2, tipo: 'Volume', valor: 3120, intensidade: 'moderado' },
    { id: 3, tipo: 'Sinal Oracular', valor: 'Lua Cheia', intensidade: 'espiritual' }
  ];

  sinais.forEach(sinal => {
    const div = document.createElement('div');
    div.className = 'sinal-card';
    div.innerHTML = `
      <h3>${sinal.tipo}</h3>
      <p>Valor: <strong>${sinal.valor}</strong></p>
      <p>Intensidade: <em>${sinal.intensidade}</em></p>
    `;
    sinaisContainer.appendChild(div);
  });

  // Animação cósmica no ícone de gráficos
  if (chartIcon) {
    chartIcon.style.transition = 'transform 0.6s ease';
    chartIcon.addEventListener('mouseenter', () => {
      chartIcon.style.transform = 'rotate(10deg) scale(1.1)';
    });
    chartIcon.addEventListener('mouseleave', () => {
      chartIcon.style.transform = 'rotate(0deg) scale(1)';
    });
  }

  // Atualização periódica dos sinais (simulado)
  setInterval(() => {
    const novo = document.createElement('div');
    novo.className = 'sinal-card novo-sinal';
    novo.innerHTML = `
      <h3>Sinal Novo</h3>
      <p>Clarinha sussurra: <strong>Foco em Saturno</strong></p>
      <p>Intensidade: <em>celestial</em></p>
    `;
    sinaisContainer.insertBefore(novo, sinaisContainer.firstChild);
    setTimeout(() => novo.classList.add('ativo'), 300);
  }, 8000);
});
