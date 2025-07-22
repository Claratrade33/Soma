class ClaraVerseSystem {
    constructor() {
        this.estrategiaAtiva = false;
        this.modoAutomatico = false;
        this.dadosMercado = {};
        this.contextoAtivo = 'oraculo';
        this.updateInterval = null;
        this.autoTradingInterval = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initContextos();
        this.startRealTimeUpdates();
        this.setupAnimations();
    }

    setupEventListeners() {
        // Contextos
        document.querySelectorAll('.btn-contexto').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.trocarContexto(e.target.dataset.contexto);
            });
        });

        // Botões principais
        document.getElementById('consultarIA')?.addEventListener('click', () => this.consultarIA());
        document.querySelector('.btn-entrada')?.addEventListener('click', () => this.definirEntrada());
        document.querySelector('.btn-stop')?.addEventListener('click', () => this.definirStop());
        document.querySelector('.btn-alvo')?.addEventListener('click', () => this.definirAlvo());
        document.querySelector('.btn-executar')?.addEventListener('click', () => this.executarOperacao());
        document.querySelector('.btn-auto')?.addEventListener('click', () => this.toggleModoAutomatico());
        document.querySelector('.btn-config')?.addEventListener('click', () => {
            window.location.href = '/configurar';
        });

        // Hotkeys
        document.addEventListener('keydown', (e) => this.handleHotkeys(e));
    }

    handleHotkeys(e) {
        if (e.ctrlKey) {
            switch(e.key) {
                case '1': this.trocarContexto('oraculo'); break;
                case '2': this.trocarContexto('cosmo'); break;
                case '3': this.trocarContexto('inteligencia'); break;
                case 'Enter': this.consultarIA(); break;
            }
        }
    }

    setupAnimations() {
        // Efeito de typing para respostas da IA
        this.typeWriter = {
            speed: 30,
            isTyping: false
        };

        // Animações de preço
        this.priceAnimator = new PriceAnimator();
    }

    trocarContexto(novoContexto) {
        this.contextoAtivo = novoContexto;
        const