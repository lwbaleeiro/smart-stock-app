import boto3
import io
import urllib.parse
import os
import logging
import pandas as pd
from app.processing.feature_engineering import create_prophet_features
from app.ml.trainer import train_models_for_products
from app.ml.predictor import generate_predictions
from app.core.database import SessionLocal
from app.core.crud import save_products_to_db, save_predictions_to_db

# Configurar logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def handler(event, context):
    """
    Lambda handler para executar o pipeline de ML.
    Acionado por evento S3 Object Created (processed/sales_...).
    """
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    logger.info(f"Evento recebido para: s3://{bucket}/{key}")

    # Verificar se é um arquivo de vendas
    if "sales" not in key:
        logger.info("Não é um arquivo de vendas. Ignorando.")
        return

    try:
        # Derivar chave do arquivo de produtos (assumindo mesmo timestamp)
        # processed/sales_{ts}.parquet -> processed/products_{ts}.parquet
        products_key = key.replace("sales", "products")
        
        logger.info(f"Baixando arquivos: {key} e {products_key}")

        # Download Sales
        sales_obj = s3_client.get_object(Bucket=bucket, Key=key)
        sales_df = pd.read_parquet(io.BytesIO(sales_obj['Body'].read()))

        # Download Products
        products_obj = s3_client.get_object(Bucket=bucket, Key=products_key)
        products_df = pd.read_parquet(io.BytesIO(products_obj['Body'].read()))

        # Iniciar sessão do banco
        db = SessionLocal()
        try:
            # 1. Salvar produtos no banco
            save_products_to_db(db, products_df)

            # 2. Feature Engineering
            logger.info("Criando features para o Prophet...")
            feature_dfs = create_prophet_features(sales_df)

            # 3. Treinamento
            logger.info("Treinando modelos...")
            trained_models = train_models_for_products(feature_dfs)

            # 4. Previsão
            logger.info("Gerando previsões...")
            predictions = generate_predictions(trained_models, days_to_predict=90)

            # 5. Salvar previsões no banco
            logger.info("Salvando previsões no banco...")
            for product_id, forecast_df in predictions.items():
                save_predictions_to_db(db, int(product_id), forecast_df)

            # 6. Salvar previsões no S3 (Data Lake)
            logger.info("Salvando previsões no S3...")
            timestamp = key.split('_')[-1].replace('.parquet', '') # Extrair timestamp do nome do arquivo
            
            for product_id, forecast_df in predictions.items():
                # Estrutura: predictions/forecast_{ts}_{product_id}.parquet
                # Ou melhor: predictions/{ts}/forecast.parquet (com todos)
                pass
            
            # Vamos salvar um arquivo único com todas as previsões
            all_predictions = []
            for pid, df in predictions.items():
                df['product_id'] = pid
                all_predictions.append(df)
            
            if all_predictions:
                final_df = pd.concat(all_predictions)
                parquet_buffer = io.BytesIO()
                final_df.to_parquet(parquet_buffer, index=False)
                parquet_buffer.seek(0)
                
                output_key = f"predictions/forecast_{timestamp}.parquet"
                s3_client.upload_fileobj(parquet_buffer, bucket, output_key)
                logger.info(f"Previsões salvas em: s3://{bucket}/{output_key}")

        finally:
            db.close()

        return {
            'statusCode': 200,
            'body': "Pipeline de ML executado com sucesso."
        }

    except Exception as e:
        logger.error(f"Erro no pipeline de ML: {e}")
        raise e
