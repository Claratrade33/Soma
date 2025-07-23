document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    socket.on('connect', () => {
        socket.emit('subscribe_market');
    });

    socket.on('market_update', data => {
        updateCryptoTable(data.crypto);
        updateBrTable(data.brazilian);
    });

    function createTableRow(cells) {
        const tr = document.createElement('tr');
        tr.innerHTML = cells.map(cell => `<td>${cell}</td>`).join('');
        return tr;
    }

    function updateCryptoTable(crypto) {
        const tbody = document.querySelector('#crypto-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        for (let sym in crypto) {
            const d = crypto[sym];
            const tr = createTableRow([sym, d.price.toFixed(2), '-', '-', '-']);
            tbody.appendChild(tr);
        }
    }

    function updateBrTable(br) {
        const tbody = document.querySelector('#br-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        for (let idx in br) {
            const d = br[idx];
            const tr = createTableRow([idx, d.price.toFixed(2), '-']);
            tbody.appendChild(tr);
        }
    }

    const analyzeForm = document.getElementById('analyze-form');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', async e => {
            e.preventDefault();
            const symbol = analyzeForm.symbol.value;

            try {
                const res = await fetch('/api/intelligent_analysis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol })
                });

                if (!res.ok) throw new Error('Erro na análise');

                const body = await res.json();
                document.getElementById('analysis-output').innerText = JSON.stringify(body, null, 2);
            } catch (error) {
                alert(`Erro: ${error.message}`);
            }
        });
    }

    const tradeForm = document.getElementById('trade-form');
    if (tradeForm) {
        tradeForm.addEventListener('submit', async e => {
            e.preventDefault();
            const symbol = tradeForm['trade-symbol'].value;
            const side = tradeForm.side.value;
            const qty = tradeForm.quantity.value;

            try {
                const res = await fetch('/api/execute_trade', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, side, quantity: qty })
                });

                const b = await res.json();
                if (b.success) {
                    alert(`✅ Trade executado com sucesso!\nPreço: ${b.price.toFixed(2)}\nP&L: ${b.pnl.toFixed(2)}`);
                    location.reload();
                } else {
                    alert(`❌ Erro: ${b.error}`);
                }
            } catch (error) {
                alert(`Erro: ${error.message}`);
            }
        });
    }
});