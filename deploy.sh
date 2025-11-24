#!/bin/bash

# Script de Deploy para o Smart Stock
# Requisitos: AWS CLI configurado, Docker, Terraform, Zip

set -e

PROJECT_NAME="smart-stock"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT_NAME}-api"

echo "--- Iniciando Deploy ---"

# 1. Empacotar Lambdas
echo "--- Empacotando Lambdas ---"
# Criar um zip temporário contendo 'app' e 'lambdas'
# Nota: Em um ambiente real, instalaríamos dependências em uma pasta 'package'
# Aqui assumimos que as dependências (pandas, etc) estão na Layer ou na imagem base da Lambda
# Para o MVP e Terraform validation, criamos um zip simples do código
if [ -f infrastructure/lambda.zip ]; then
    rm infrastructure/lambda.zip
fi

# Zipar o conteúdo necessário
# Precisamos que 'app' e 'lambdas' estejam na raiz do zip para os imports funcionarem
zip -r infrastructure/lambda.zip app lambdas

echo "--- Lambdas empacotadas em infrastructure/lambda.zip ---"

# 2. Build & Push Docker Image
echo "--- Construindo Imagem Docker ---"
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Verificar se o repositório existe (o Terraform cria, mas precisamos dele para o push inicial se o Terraform depender da imagem)
# Para evitar o problema do "ovo e a galinha", o Terraform cria o repo ECR primeiro.
# Se for o primeiro deploy, pode falhar o App Runner se a imagem não existir.
# Estratégia: Rodar Terraform Target ECR -> Push Image -> Rodar Terraform Full

echo "--- Provisionando ECR (Terraform Target) ---"
cd infrastructure
terraform init
terraform apply -target=aws_ecr_repository.api -auto-approve
cd ..

echo "--- Build & Push ---"
docker build -t ${PROJECT_NAME}-api .
docker tag ${PROJECT_NAME}-api:latest ${ECR_REPO}:latest
docker push ${ECR_REPO}:latest

echo "--- Imagem enviada para o ECR ---"

# 3. Aplicar Infraestrutura Completa
echo "--- Aplicando Terraform Completo ---"
cd infrastructure
terraform apply -auto-approve
cd ..

echo "--- Deploy Concluído! ---"
echo "Verifique o output do Terraform para a URL da API."
