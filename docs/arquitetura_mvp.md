## **Arquitetura do MVP**

```
┌─────────────────┐
│   Upload CSV    │ (Interface simples ou API)
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│   Lambda/FastAPI                        │
│   • Valida CSV                          │
│   • Gera ID único por upload            │
│   • Salva no S3 (raw)                   │
└────────┬────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────────────────────┐x
│   S3 (Data Lake Simples)                               │
│   Estrutura:                                           │
│   s3://bucket/                                         │
│     raw/{company-name}/{cnpj}/{ano}/{mes}/{dia}/       │
│       vendas_{timestamp}.csv                           │
│       vendas_itens{timestamp}.csv                      │
│       produtos_{timestamp}.csv                         │
│     processed/{company-name}/{cnpj}/{ano}/{mes}/       │
│       features_{date}.parquet                          │
│     predictions/{company-name}/{cnpj}/{ano}/{mes}/     │
│       forecast_{date}.parquet                          │
└────────┬───────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│   Lambda/ECS (Processing)               │
│   • Lê CSV do S3                        │
│   • Limpeza/validação (Pandas)          │       
│   • Salva em processed/                 │
└────────┬────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│   Lambda/ECS (ML Pipeline)              │
│   • Carrega dados processados           │
│   • Treina com Prophet                  │
│   • Gera previsões (30/60/90 dias)      │
│   • Salva em predictions/               │
└────────┬────────────────────────────────┘
         │
         │
         ↓
┌─────────────────────────────────────────┐
│   FastAPI (API)                         │
│   Endpoints:                            │
│   • POST /upload                        │
│   • GET /predictions/{cnpj}             │
│   • GET /products/{cnpj}                │
│   • GET /sales/{cnpj}                   │
│   • GET /metrics                        │
└─────────────────────────────────────────┘
```

---

## **Stack Tecnológico Simplificado**

| Componente | Tecnologia | Por quê |
|------------|------------|---------|
| **Backend/API** | FastAPI + Uvicorn | Rápido, async, fácil documentação |
| **Processing** | Pandas + Polars | Pandas = flexibilidade, Polars = performance |
| **ML** | Prophet + scikit-learn | Prophet = séries temporais fácil, sklearn = complementos |
| **Storage** | S3 (Parquet) | Barato, durável, formato colunar eficiente |
| **Database** | PostgreSQL (RDS) | SQL confiável, jsonb para flexibilidade |
| **Compute** | Lambda (início) → ECS Fargate (escala) | Serverless simples, depois containers |
| **Orquestração** | EventBridge + Lambda | Gatilhos simples sem Airflow |
| **Deploy** | Docker + ECR + ECS | Containerizado, fácil replicar |
| **IaC** | Terraform (opcional) ou AWS CDK | Versionamento de infra |

---

## **Estrutura do Projeto**

```
quantyfy-app-mvp/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/
│   │   │   ├── upload.py        # POST /upload
│   │   │   ├── predictions.py   # GET /predictions
│   │   │   └── health.py        # Healthcheck
│   │   └── dependencies.py      # Auth, DB connection
│   │
│   ├── core/
│   │   ├── config.py            # Settings (pydantic)
│   │   ├── s3.py                # S3 utils
│   │   └── database.py          # SQLAlchemy models
│   │
│   ├── processing/
│   │   ├── cleaner.py           # Limpeza de dados
│   │   ├── validator.py         # Validação CSV
│   │   └── feature_engineering.py
│   │
│   ├── ml/
│   │   ├── prophet_model.py     # Wrapper Prophet
│   │   ├── trainer.py           # Treino de modelos
│   │   ├── predictor.py         # Inferência
│   │   └── evaluator.py         # Métricas (MAPE, RMSE)
│   │
│   └── utils/
│       ├── logger.py
│       └── metrics.py
│
├── lambdas/                     # Funções Lambda (se usar)
│   ├── upload_handler/
│   ├── process_handler/
│   └── predict_handler/
│
├── infrastructure/              # Terraform ou CDK
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── tests/
│   ├── test_api.py
│   ├── test_processing.py
│   └── test_ml.py
│
├── Dockerfile
├── docker-compose.yml           # Local dev
├── requirements.txt
└── README.md
```

---