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
      historico.unshift({
        tipo: tipo === "buy" ? "Compra" : tipo === "sell" ? "Venda" : (tipo === "suggest" ? "Sugestão IA" : "Automático"),
        ativo: "BTCUSDT",
        valor: document.getElementById('cv-qtd').value || "0.001",
        preco: "67700",
        hora: new Date().toLocaleTimeString().slice(0,5)
      });
      renderHistorico();
      if (tipo === "suggest") {
        document.getElementById('cv-ia-output').innerHTML =
          "<b>Entrada:</b> 67600 | <b>Alvo:</b> 68000 | <b>Stop:</b> 67450 <br><b>Confiança:</b> 87%<br><i>Análise IA: O mercado mostra tendência de alta com suporte em 67450 e RSI saudável.</i>";
      }
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

  // Gráfico TradingView com Lightweight Charts
  const chartEl = document.getElementById('cv-chart');
  if (chartEl) {
    const chart = LightweightCharts.createChart(chartEl, {
      width: chartEl.offsetWidth,
      height: 240,
      layout: { background: { color: '#171725' }, textColor: '#eee' },
      grid: { vertLines: { color: '#24243c' }, horzLines: { color: '#24243c' } }
    });
    const candleSeries = chart.addCandlestickSeries();
    // Simula dados (coloque fetch de dados reais se quiser)
    const now = Math.floor(Date.now()/1000);
    let c = 67600;
    const candles = [];
    for(let i=60;i>0;i--) {
      const t = now-i*60;
      const o = c + Math.random()*30-15;
      const h = o + Math.random()*10;
      const l = o - Math.random()*10;
      const close = o + Math.random()*8-4;
      candles.push({ time: t, open: o, high: h, low: l, close });
      c = close;
    }
    candleSeries.setData(candles);
    // Atualiza preço
    document.getElementById('cv-preco').innerText = candles[candles.length-1].close.toFixed(2);
    document.getElementById('cv-volume').innerText = (Math.random()*1500+3000).toFixed(0);
    document.getElementById('cv-rsi').innerText = (Math.random()*30+50).toFixed(2);
    window.addEventListener('resize', ()=>chart.resize(chartEl.offsetWidth,240));
  }
});
