# Desafio Desenvolvedor Odoo Paycon

Este repositório fornece um ambiente **Odoo 14** local totalmente reprodutível utilizando **Docker Compose**, com **bootstrap automático** na sua primeira inicialização.

O objetivo é ter um setup **limpo, organizado, com tratamento de erros e visual responsivo.**


## Entregável 

- Odoo 14 
- PostgreSQL
- Bootstrap automático na primeira inicialização:
  - Criação do banco e instalação do módulo **Contacts**
  - Carregamento do idioma **Português (Brasil)**
- Estrutura base para criação de módulos personalizados, com um módulo personalizado já adicionado.
- Ambiente configurado através de variáveis de ambiente (.env)

## 🧱 Estrutura do projeto

```
.
├── docker-compose.yml
├── .env.example
├── .env                        # não versionado
├── README.md
├── data/
│   └── odoo/                   # filestore e estado do Odoo
└── odoo/
|   ├── config/
|   │   └── odoo.conf
|   ├── addons/                 # módulos customizados
|   └── entrypoint/
|       └── odoo-entrypoint.sh
└── flask_app/
|   ├── app/
|   │   └── templates/
|   |       └── base.html       # template com front-end base
|   |       └── index.html      # template com front-end para visualização dos dados e gráficos 
|   │   └── `__init__.py`       # módulo de inicialização do app
|   │   └── config.py           # módulo para controle das configurações do app
|   │   └── metrics.py          # módulo com métodos para cálculo das métricas dos gráficos
|   │   └── odoo_jsonrpc.py     # módulo com métodos para conexão com a API do Odoo 14
|   │   └── routes.py           # módulo que define rotas do APP e renderiza templates
|   ├── addons/                 # módulos customizados
|   ├── Dockerfile
|   └── requirements.txt
```

## Variáveis de ambiente

Crie um `.env` na raiz do projeto (mesmo diretório do `docker-compose.yml`).

Exemplo mínimo:

```env
# POSTGRES
POSTGRES_DB=odoo14_local
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo

# ODOO (conexão com o Postgres)
DB_HOST=db
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=odoo
DB_NAME=odoo14_local
DB_FILTER=^odoo14_local$
ADMIN_PASSWD=admin
LIST_DB=False

# FLASK (Flask chama o Odoo dentro da rede do Docker)
ODOO_URL=http://odoo:8069
ODOO_DB=odoo14_local
ODOO_USER=admin@example.com
ODOO_PASSWORD=admin

# opcional
LOG_LEVEL=INFO

### Observação importante

- Configurações variáveis (DB, filtros, etc.) **não ficam no `odoo.conf`**
- Tudo isso é passado via **CLI** no entrypoint
- Evita template de config e reduz complexidade

---

## ▶️ Como executar

### 1. Realizar build do projeto

```bash
# Crie a pasta data/odoo para bind montado
mkdir -p data/odoo

# Execute o build
docker compose up -d --build 
```

### 2. Acompanhar logs

```bash
docker compose logs -f
```

Na **primeira execução**, você verá:
- criação do banco
- instalação do Contacts
- carregamento do idioma pt-BR

### 3. Acessar no navegador

```
http://localhost:8069 -- Odoo 14
```

```
http://localhost:5000 -- App Dashboard
```

## Carregar contatos de demonstração

Para carregar contatos e visualizar no dashboard foi criada uma feature que gera automaticamente diversos contatos no Odoo.

### Como acessar esta feature?

1. Acesse o módulo de contatos no Odoo como Administrador
2. Vá no menu `contatos` e clique em `Generate Demo Contacts`
3. Preencha a quantidade e desmarque o botão **Dry Run**
4. Clique no botão **Generate** e os contatos serão gerados.

### Detalhes da feature

* O booleano **Dry Run** não permite a geração dos contatos, apenas demonstra se irá rodar com sucesso ou não.
* O booleano **Force Recreate** deleta os contatos que estão com a categoria `Seed: Paycon Interview` e cria novos contatos.
* Por padrão, se existirem contatos criados pela feature e tentar gerar novos um erro irá ser gerado, informando que é necessário marcar o booleano **Force Recreate**.
* **Active e Company Ratios** são fatores de multiplicação criados para definir um número específico de contatos gerados que serão clientes ativos e clientes do tipo empresa.

