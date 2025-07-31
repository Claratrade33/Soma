 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/static/js/ dashboard.js b/static/js/ dashboard.js
deleted file mode 100644
index d8d0c7337d565e3f6cd81e8ad8e32fd3b9700afd..0000000000000000000000000000000000000000
--- a/static/js/ dashboard.js	
+++ /dev/null
@@ -1,40 +0,0 @@
-document.addEventListener('DOMContentLoaded', () => {
-  // Histórico local (simulação visual)
-  let historico = [];
-
-  function renderHistorico() {
-    const ordensList = document.getElementById('ordens-list');
-    if (!ordensList) return;
-    ordensList.innerHTML = "";
-    for (let o of historico) {
-      let li = document.createElement('li');
-      li.innerHTML = `<b>${o.tipo}</b> ${o.ativo} - ${o.valor} @ ${o.preco} <span style="color:#aaa">${o.hora}</span>`;
-      ordensList.appendChild(li);
-    }
-  }
-
-  window.confirmarOrdem = function(tipo) {
-    let msg = "Tem certeza que deseja executar essa ordem?";
-    if (tipo === "buy") msg = "Confirmar compra?";
-    if (tipo === "sell") msg = "Confirmar venda?";
-    if (tipo === "suggest") msg = "Pedir sugestão para a IA?";
-    if (tipo === "auto") msg = "Ativar modo automático?";
-    if (confirm(msg)) {
-      let valor = document.getElementById("qtd_input")?.value || "0.001";
-      historico.unshift({
-        tipo: tipo === "buy" ? "Compra" :
-              tipo === "sell" ? "Venda" :
-              tipo === "suggest" ? "Sugestão IA" : "Automático",
-        ativo: "BTCUSDT",
-        valor: valor,
-        preco: "ao vivo",
-        hora: new Date().toLocaleTimeString().slice(0,5)
-      });
-      renderHistorico();
-      alert("Ordem executada!");
-      // Para ordens reais, faça requisição Ajax para /executar_ordem
-    }
-  };
-
-  renderHistorico();
-});
diff --git a/static/js/dashboard.js b/static/js/dashboard.js
new file mode 100644
index 0000000000000000000000000000000000000000..9197994a6d6ae99c82ccddb1a57d461262c210bd
--- /dev/null
+++ b/static/js/dashboard.js
@@ -0,0 +1,78 @@
+document.addEventListener('DOMContentLoaded', () => {
+  // Histórico local (simulação visual)
+  let historico = [];
+
+  async function atualizarHistorico() {
+    try {
+      const resp = await fetch("/historico");
+      if (resp.ok) {
+        historico = await resp.json();
+        renderHistorico();
+      }
+    } catch (e) {
+      console.error("Erro ao atualizar histórico", e);
+    }
+  }
+
+  function renderHistorico() {
+    const corpo = document.querySelector('#ordens-table tbody');
+    if (!corpo) return;
+    corpo.innerHTML = "";
+    for (let o of historico) {
+      const tr = document.createElement('tr');
+      const tipoLower = (o.tipo || '').toLowerCase();
+      let tipoClass = '';
+      if (tipoLower.includes('compra')) tipoClass = 'compra';
+      if (tipoLower.includes('venda')) tipoClass = 'venda';
+      tr.innerHTML = `
+        <td class="tipo-${tipoClass}">${o.tipo}</td>
+        <td>${o.ativo}</td>
+        <td>${o.valor}</td>
+        <td>${o.preco}</td>
+        <td>${o.hora}</td>`;
+      corpo.appendChild(tr);
+    }
+  }
+
+  window.confirmarOrdem = async function(tipo) {
+    let msg = "Tem certeza que deseja executar essa ordem?";
+    if (tipo === "buy") msg = "Confirmar compra?";
+    if (tipo === "sell") msg = "Confirmar venda?";
+    if (tipo === "suggest") msg = "Pedir sugestão para a IA?";
+    if (tipo === "auto") msg = "Ativar modo automático?";
+    if (confirm(msg)) {
+      let valor = document.getElementById("qtd_input")?.value || "0.001";
+      if (tipo === "buy" || tipo === "sell") {
+        const form = new URLSearchParams();
+        form.append("tipo", tipo === "buy" ? "compra" : "venda");
+        form.append("quantidade", valor);
+        try {
+          const resp = await fetch("/executar_ordem", {
+            method: "POST",
+            headers: {"Content-Type": "application/x-www-form-urlencoded"},
+            body: form.toString()
+          });
+          if (resp.ok) {
+            alert("Ordem executada!");
+            await atualizarHistorico();
+          } else {
+            alert("Erro ao executar ordem");
+          }
+        } catch (e) {
+          console.error("Erro ao executar ordem", e);
+        }
+      } else {
+        historico.unshift({
+          tipo: tipo === "suggest" ? "Sugestão IA" : "Automático",
+          ativo: "BTCUSDT",
+          valor: valor,
+          preco: "ao vivo",
+          hora: new Date().toLocaleTimeString().slice(0,5)
+        });
+        renderHistorico();
+      }
+    }
+  };
+
+  atualizarHistorico();
+});
diff --git a/static/style.css b/static/style.css
index c7249b73f6c47ff4282e45bf8400a211c1376a14..752af634f53732b3227ccd5f29ac05961ecd21c6 100644
--- a/static/style.css
+++ b/static/style.css
@@ -121,49 +121,61 @@ input:focus { background: #292047; }
   border-radius: 12px;
   border: none;
   margin-bottom: 13px;
   font-size: 1.17rem;
   font-weight: 700;
   transition: all 0.12s;
   cursor: pointer;
   letter-spacing: 1.2px;
   color: #fff;
   background: linear-gradient(90deg,#19e09e,#6f6ffc);
   box-shadow: 0 0 8px #19e09e80;
 }
 .btn.buy { background: linear-gradient(90deg,#00ffd6,#52aaff); }
 .btn.sell { background: linear-gradient(90deg,#ff3c6e,#f49727); box-shadow: 0 0 8px #ff3c6e70; }
 .btn.suggest { background: linear-gradient(90deg,#42e9f5,#9a35ff); box-shadow: 0 0 8px #42e9f570; }
 .btn.auto { background: linear-gradient(90deg,#f3c742,#fc7ea2); color: #222; box-shadow: 0 0 8px #f3c74270; }
 .btn:active { transform: scale(0.98); filter: brightness(0.97); }
 
 .historico-title {
   font-size: 1.11rem;
   margin: 20px 0 8px 0;
   color: #12e3ff;
   letter-spacing: 0.6px;
 }
 
-#ordens-list {
-  list-style: none;
-  padding: 0;
-  margin: 0;
+#ordens-table {
+  width: 100%;
+  border-collapse: collapse;
   font-size: 0.99rem;
   color: #eee;
 }
-#ordens-list li { margin-bottom: 6px; }
+#ordens-table th,
+#ordens-table td {
+  padding: 6px 8px;
+  text-align: left;
+}
+#ordens-table thead th {
+  color: #12e3ff;
+  border-bottom: 1px solid #3c2a5d;
+  font-weight: 700;
+}
+#ordens-table tbody tr:nth-child(odd) { background: #211742; }
+#ordens-table tbody tr:nth-child(even) { background: #1a1336; }
+#ordens-table td.tipo-compra { color: #19e09e; font-weight: 700; }
+#ordens-table td.tipo-venda { color: #ff3c6e; font-weight: 700; }
 
 .alert.danger {
   background: #ff3c3c;
   color: #fff;
   border-radius: 8px;
   padding: 14px;
   text-align: center;
   margin: 20px 18vw 0 18vw;
   font-size: 1.13rem;
 }
 
 @media (max-width:950px) {
   .painel-container { flex-direction: column; padding: 1.2rem; gap: 1.1rem; }
   .grafico-section, .carteira-section { min-width: 0; padding: 1.2rem; }
   header nav { flex-direction: column; gap: 18px; padding: 26px 3vw 12px 3vw; }
 }
diff --git a/templates/painel_operacao.html b/templates/painel_operacao.html
index 17e92f2d86225b649fd3100cd47bc9eb1f001c66..d5e52a9a789ffb6b35f46021e34e7f2269301e3b 100644
--- a/templates/painel_operacao.html
+++ b/templates/painel_operacao.html
@@ -46,31 +46,42 @@
                   "studies": [
                     "STD;Moving Average",
                     "STD;RSI"
                   ],
                 });
             </script>
             <div class="info-row">
                 <span>Par: <b>BTC/USDT</b></span>
                 <span style="margin-left:16px;">Mercado em tempo real</span>
             </div>
         </section>
         <!-- Carteira e Painel de Ordens -->
         <aside class="carteira-section">
             <h2 class="carteira-title">Carteira</h2>
             <div class="carteira-saldo">
                 <div>BTC Spot: <span id="saldo-btc">{{ saldo_btc }}</span></div>
                 <div>USDT Spot: <span id="saldo-usdt">{{ saldo_usdt }}</span></div>
                 <div>USDT Futuros: <span id="saldo-futures-usdt">{{ saldo_futures_usdt }}</span></div>
             </div>
             <input type="number" step="any" min="0" id="qtd_input" placeholder="Quantidade">
             <button class="btn buy" onclick="confirmarOrdem('buy')">Comprar</button>
             <button class="btn sell" onclick="confirmarOrdem('sell')">Vender</button>
             <button class="btn suggest" onclick="confirmarOrdem('suggest')">Sugestão IA</button>
             <button class="btn auto" onclick="confirmarOrdem('auto')">Automático</button>
             <h3 class="historico-title">Histórico de Ordens</h3>
-            <ul id="ordens-list"></ul>
+            <table id="ordens-table">
+                <thead>
+                    <tr>
+                        <th>Tipo</th>
+                        <th>Ativo</th>
+                        <th>Qtd.</th>
+                        <th>Preço</th>
+                        <th>Hora</th>
+                    </tr>
+                </thead>
+                <tbody></tbody>
+            </table>
         </aside>
     </div>
-    <script src="{{ url_for('static', filename='dashboard.js') }}"></script>
+    <script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
 </body>
 </html>
 
EOF
)
