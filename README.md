# Constroiverse

Constroiverse é um ecossistema em desenvolvimento que pretende conectar
clientes, profissionais e fornecedores da construção civil em um único
ambiente digital. A proposta é oferecer um "iFood da construção" com
inteligência artificial para orçamentos, logística e gestão de obras.

Este repositório já disponibiliza um backend Flask funcional com
autenticação JWT, persistência em banco de dados e uma camada inicial de
IA baseada na API da OpenAI. Com ele é possível registrar usuários,
gerar tokens de acesso, criar obras e solicitar respostas da assistente
Clarice. O objetivo desta etapa é fornecer um esqueleto sólido sobre o
qual os módulos específicos de cada perfil (cliente, mestre de obra,
lojista, engenheiro etc.) possam ser evoluídos.

## 🚀 Funcionalidades previstas

- **IA Clarice** – integrações futuras com a API da OpenAI para
  responder dúvidas, auxiliar em orçamentos e sugerir materiais.
- **Painéis por perfil** – telas diferentes para clientes, lojistas e
  profissionais da obra.
- **Financeiro** – controle de orçamento, previsão de gastos e cálculo
  de ROI por obra.
- **Logística** – uso da API do Google Maps para rotas de entrega e
  visualização em tempo real.
- **Orçamentos dinâmicos** – geração de propostas com base em listas de
  insumos ou upload de projetos.

## 🛠 Instalação

1. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copie o arquivo de exemplo de variáveis de ambiente e ajuste os
   valores:

   ```bash
   cp .env.example .env
   ```

3. Execute a aplicação Flask:

   ```bash
  flask --app api.py run
  ```

## 📦 Estrutura

```
static/        # arquivos estáticos (CSS, JS)
templates/     # páginas HTML
api.py         # API REST principal com JWT e rotas de obra
models.py      # modelos SQLAlchemy
users.json     # legado: usuários armazenados localmente
orders.json    # legado: histórico de ordens
```

## 🔌 Endpoints principais

A API atual disponibiliza os seguintes pontos de entrada:

| Método | Rota        | Descrição                                   |
|--------|-------------|---------------------------------------------|
| POST   | `/register` | Cria um novo usuário                        |
| POST   | `/login`    | Autentica e retorna um JWT                  |
| GET    | `/projects` | Lista obras do usuário autenticado          |
| POST   | `/projects` | Cria uma nova obra                          |
| POST   | `/budget`   | Calcula orçamento simples a partir de itens |
| POST   | `/clarice`  | Encaminha mensagem para a IA Clarice        |

Rotas `/register`, `/login` e `/chat` também possuem páginas HTML
simples para uso manual durante o desenvolvimento.

## 🔑 Variáveis de ambiente

O arquivo `.env.example` lista as principais chaves utilizadas pelo
projeto. Preencha-as com os valores corretos antes de executar em
produção.

## 🔭 Próximos passos

- CRUD completo de obras, tarefas e profissionais.
- Integração real com OpenAI e Google Maps.
- Autenticação JWT e banco PostgreSQL.
- Painéis específicos para cada perfil de usuário.
- Automação de pedidos para fornecedores parceiros.

## 📝 Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo
[`LICENSE`](LICENSE) para mais informações.

