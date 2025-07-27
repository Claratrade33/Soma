// static/js/dashboard.js

async function executarOrdem(tipo) {
    try {
        const btn = document.querySelector(`button[data-ordem="${tipo}"]`);
        if (btn) btn.disabled = true;

        const resposta = await fetch('/executar_ordem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo })
        });

        const resultado = await resposta.json();

        if (resposta.ok) {
            alert(`✅ Ordem ${tipo.toUpperCase()} executada com sucesso!`);
        } else {
            alert(`🚨 Erro: ${resultado.erro}`);
        }
    } catch (e) {
        alert(`🚨 Falha na comunicação: ${e.message}`);
    } finally {
        const btn = document.querySelector(`button[data-ordem="${tipo}"]`);
        if (btn) btn.disabled = false;
    }
}

function ativarAuto() {
    const confirmacao = confirm("Deseja mesmo ativar o modo automático de ordens?");
    if (confirmacao) {
        alert("🤖 Modo automático ativado! As ordens serão enviadas conforme os sinais da IA.");
        // Aqui você pode implementar uma lógica de polling ou socket futuramente
    }
}
