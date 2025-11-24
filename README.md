# Smart Stock App

Smart Stock App é uma plataforma de inteligência preditiva que ajuda e-commerces e empresas de varejo a prever demandas futuras, otimizando a gestão de estoque e compras.

## Arquitetura e Fluxo

A aplicação é construída em FastAPI e utiliza um pipeline de dados e ML para gerar previsões de demanda.

1.  **Upload:** O usuário envia arquivos CSV de produtos e vendas via API.
2.  **Validação e Limpeza:** Os dados são validados, limpos e salvos em um formato otimizado (Parquet). Os arquivos brutos e processados são enviados para um bucket S3.
3.  **Processamento Assíncrono:** Uma tarefa em segundo plano é iniciada para não bloquear a API.
4.  **Pipeline de ML:** A tarefa executa o pipeline de Machine Learning:
    -   Os dados de produtos são salvos no banco de dados PostgreSQL.
    -   Um modelo de previsão (Prophet) é treinado para cada produto.
    -   As previsões de demanda para os próximos 90 dias são geradas.
    -   Os resultados são salvos no banco de dados.
5.  **Consulta:** As previsões podem ser consultadas a qualquer momento através de um endpoint específico.

## Como Rodar Localmente (com Docker)

O ambiente de desenvolvimento utiliza Docker e Docker Compose para orquestrar a API e o banco de dados.

1.  **Pré-requisitos:**
    -   Docker
    -   Docker Compose

2.  **Variáveis de Ambiente:**
    -   **Banco de Dados:** As credenciais do PostgreSQL são definidas diretamente no arquivo `docker-compose.yml`. A aplicação FastAPI as recebe automaticamente.
    -   **AWS S3:** A funcionalidade de upload para o S3 requer credenciais da AWS. Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
        ```
        AWS_ACCESS_KEY_ID=SUA_ACCESS_KEY
        AWS_SECRET_ACCESS_KEY=SUA_SECRET_KEY
        AWS_REGION=sua-regiao-default (ex: us-east-1)
        S3_BUCKET_NAME=nome-do-seu-bucket
        ```
    *Observação: Sem o arquivo `.env`, os uploads para o S3 falharão, mas o restante da aplicação (incluindo o pipeline de ML e o banco de dados) funcionará.*

3.  **Execução:**
    -   Para construir e iniciar os contêineres, execute:
        ```bash
        docker-compose up --build
        ```
    -   A API estará disponível em `http://localhost:8000`.
    -   A documentação interativa (Swagger UI) estará em `http://localhost:8000/docs`.

## Endpoints da API

### Upload

-   `POST /upload`
    -   Recebe os arquivos CSV de produtos e vendas e dispara o pipeline de processamento e treinamento.
    -   **Corpo da Requisição:** `multipart/form-form-data` com os campos `products_file` e `sales_file`.
    -   **Resposta de Sucesso (200):**
        ```json
        {
          "message": "Arquivos recebidos. O processamento foi iniciado."
        }
        ```

### Predictions

-   `GET /predictions/{product_id}`
    -   Retorna a previsão de demanda para um produto específico.
    -   **Resposta de Sucesso (200):**
        ```json
        [
          {
            "ds": "2023-11-20T00:00:00",
            "yhat": 15.3,
            "yhat_lower": 12.1,
            "yhat_upper": 18.5,
            "id": 1,
            "product_id": 101
          }
        ]
        ```

### Health Check

-   `GET /health`: Verifica a saúde da aplicação.

## Como Rodar os Testes

1. **Ative o environment:**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

2. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Execute o Pytest:**
    A partir do diretório raiz do projeto, execute:
    ```bash
    python -m pytest tests/
    ```

## Estrutura do Projeto

```
smart-stock-app/
│
├── app/                         # Código da Aplicação (FastAPI + ML)
│   ├── api/                     # Rotas e Dependências
│   ├── core/                    # Configurações, DB, S3
│   ├── ml/                      # Lógica de Machine Learning (Prophet)
│   ├── processing/              # Limpeza e Validação de Dados
│   └── utils/                   # Utilitários (Logger, Metrics)
│
├── lambdas/                     # AWS Lambda Handlers
│   ├── process_handler/         # Processamento de CSV -> Parquet
│   └── predict_handler/         # Pipeline de ML (Treino + Previsão)
│
├── infrastructure/              # Infrastructure as Code (Terraform)
│   ├── main.tf                  # Definição de Recursos AWS
│   ├── variables.tf             # Variáveis
│   └── outputs.tf               # Outputs
│
├── tests/                       # Testes Automatizados
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Infraestrutura e Deploy (AWS)

O projeto utiliza **Terraform** para provisionar a infraestrutura na AWS e **App Runner** para hospedar a API.

### Recursos Provisionados
*   **AWS App Runner:** Hospedagem gerenciada da API FastAPI (escalável e seguro).
*   **S3 Bucket:** Data Lake (`raw/`, `processed/`, `predictions/`).
*   **RDS (PostgreSQL):** Banco de dados relacional.
*   **ECR:** Repositório de imagens Docker.
*   **Lambda Functions:** Processamento assíncrono e ML.

### Como Fazer o Deploy

Um script automatizado `deploy.sh` foi criado para facilitar o processo. Ele realiza as seguintes etapas:
1.  Empacota as funções Lambda.
2.  Constrói e envia a imagem Docker para o ECR.
3.  Aplica a infraestrutura via Terraform.

**Pré-requisitos:**
*   AWS CLI configurado (`aws configure`).
*   Docker em execução.
*   Terraform instalado.

**Executando o Deploy:**

```bash
# No Windows (Git Bash ou WSL)
export TF_VAR_db_password="SuaSenhaSuperSegura123"
./deploy.sh
```

Ao final, o Terraform exibirá a URL da API (App Runner) e o Endpoint do Banco de Dados.
