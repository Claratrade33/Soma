// Variáveis globais
let estrategiaAtiva = false;
let modoAutomatico = false;
let dadosMercado = {};

// Função para atualizar dados do mercado
async function atualizarDadosMercado() {
    try {
        const response = await fetch('/api/dados_mercado');
        const data = await response.json();
        
        if (data.erro) {
            console.error('Erro ao obter dados:', data.erro);
            return;
        }
        
        dadosMercado = data;
        
        // Atualizar elementos na tela
        document.getElementById('preco').textContent = parseFloat(data.preco).toFixed(2);
        document.getElementById('variacao').textContent = data.variacao + '%';
        document.getElementById('volume').textContent = data.volume;
        document.getElementById('rsi').textContent = data.rsi;
        document.getElementById('suporte').textContent = data.suporte;
        document.getElementById('resistencia').textContent = data.resistencia;
        
    } catch (error) {
        console.error('Erro na requisição:', error);
    }
}

// Função para consultar IA
async function consultarIA() {
    document.getElementById('resposta-ia').innerHTML = '🔄 Consultando a IA...';
    
    try {
        const response = await fetch('/api/sugestao_ia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: `Analise o mercado BTC/USDT com os seguintes dados:
                Preço: ${dadosMercado.preco}
                RSI: ${dadosMercado.rsi}
                Suporte: ${dadosMercado.suporte}
                Resistência: ${dadosMercado.resistencia}
                Dê uma recomendação de entrada, stop e alvo.`
            })
        });
        
        const data = await response.json();
        
        if (data.erro) {
            document.getElementById('resposta-ia').innerHTML = '❌ Erro: ' + data.erro;
        } else {
            document.getElementById('resposta-ia').innerHTML = data.resposta;
        }
        
    } catch (error) {
        document.getElementById('resposta-ia').innerHTML = '❌ Erro na consulta à IA';
        console.error('Erro:', error);
    }
}

// Função para executar operação
async function executarOperacao(tipo) {
    if (!confirm(`Tem certeza que deseja executar: ${tipo}?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/executar_operacao', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tipo: tipo,
                quantidade: 0.001 // Quantidade padrão
            })
        });
        
        const data = await response.json();
        
        if (data.erro) {
            alert('Erro: ' + data.erro);
        } else {
            alert('Sucesso: ' + data.mensagem);
            atualizarSaldo();
        }
        
    } catch (error) {
        alert('Erro na operação');
        console.error('Erro:', error);
    }
}

// Função para atualizar saldo
async function atualizarSaldo() {
    try {
        const response = await fetch('/api/saldo');
        const data = await response.json();
        
        if (!data.erro) {
            document.querySelector('.saldo').innerHTML = `💰 Saldo: ${parseFloat(data.saldo).toFixed(2)} USDT`;
        }
    } catch (error) {
        console.error('Erro ao atualizar saldo:', error);
    }
}

// Event listeners para os botões
document.addEventListener('DOMContentLoaded', function() {
    // Botão consultar IA
    document.getElementById('consultarIA').addEventListener('click', consultarIA);
    
    // Botões de operação
    document.querySelector('.btn-entrada').addEventListener('click', () => {
        estrategiaAtiva = true;
        alert('📍 Posição de entrada marcada!');
    });
    
    document.querySelector('.btn-stop').addEventListener('click', () => {
        executarOperacao('stop');
    });
    
    document.querySelector('.btn-alvo').addEventListener('click', () => {
        alert('🎯 Alvo definido! Aguardando execução...');
    });
    
    document.querySelector('.btn-executar').addEventListener('click', () => {
        if (estrategiaAtiva) {
            const acao = confirm('Deseja COMPRAR (OK) ou VENDER (Cancelar)?');
            executarOperacao(acao ? 'comprar' : 'vender');
        } else {
            alert('❌ Defina uma estratégia primeiro!');
        }
    });
    
    document.querySelector('.btn-auto').addEventListener('click', () => {
        modoAutomatico = !modoAutomatico;
        const botao = document.querySelector('.btn-auto');
        
        if (modoAutomatico) {
            botao.textContent = '🔴 PARAR AUTO';
            botao.style.backgroundColor = '#ff4444';
            alert('🤖 Modo automático ATIVADO!');
            iniciarModoAutomatico();
        } else {
            botao.textContent = '🤖 AUTOMÁTICO';
            botao.style.backgroundColor = '#4CAF50';
            alert('⏹️ Modo automático DESATIVADO!');
        }
    });
    
    document.querySelector('.btn-config').addEventListener('click', () => {
        window.location.href = '/configurar';
    });
    
    // Atualizar dados a cada 5 segundos
    setInterval(atualizarDadosMercado, 5000);
    
    // Primeira atualização
    atualizarDadosMercado();
    atualizarSaldo();
});

// Função do modo automático
function iniciarModoAutomatico() {
    if (!modoAutomatico) return;
    
    // Lógica básica do modo automático
    setTimeout(() => {
        if (modoAutomatico && dadosMercado.rsi) {
            if (dadosMercado.rsi < 30) {
                console.log('RSI baixo, sinal de compra');
                // Executar compra automática
            } else if (dadosMercado.rsi > 70) {
                console.log('RSI alto, sinal de venda');
                // Executar venda automática
            }
        }
        iniciarModoAutomatico(); // Recursão para continuar
    }, 10000); // A cada 10 segundos
}