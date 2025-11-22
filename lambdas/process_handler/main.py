import boto3
import io
import urllib.parse
import os
import logging
from app.processing.validator import validate_csv, PRODUCT_COLUMNS, SALES_COLUMNS
from app.processing.cleaner import clean_products_data, clean_sales_data
from app.core.config import settings

# Configurar logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def handler(event, context):
    """
    Lambda handler para processar arquivos CSV enviados para o S3.
    Acionado por evento S3 Object Created.
    """
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    logger.info(f"Iniciando processamento do arquivo: s3://{bucket}/{key}")

    try:
        # Identificar tipo de arquivo
        if "products" in key:
            file_type = "products"
            columns = PRODUCT_COLUMNS
            cleaner_func = clean_products_data
        elif "sales" in key:
            file_type = "sales"
            columns = SALES_COLUMNS
            cleaner_func = clean_sales_data
        else:
            logger.warning(f"Tipo de arquivo desconhecido: {key}. Ignorando.")
            return

        # Download do arquivo
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read()
        file_obj = io.BytesIO(file_content)

        # Validar
        is_valid, message = validate_csv(file_obj, columns)
        if not is_valid:
            logger.error(f"Arquivo inválido: {message}")
            # Opcional: Mover para bucket de erro ou notificar
            return

        # Limpar
        df = cleaner_func(file_obj)
        
        # Converter para Parquet
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)

        # Definir caminho de saída
        # Ex: raw/products_2023...csv -> processed/products_2023...parquet
        filename = os.path.basename(key)
        filename_no_ext = os.path.splitext(filename)[0]
        output_key = f"processed/{filename_no_ext}.parquet"

        # Upload
        s3_client.upload_fileobj(parquet_buffer, bucket, output_key)
        logger.info(f"Arquivo processado salvo em: s3://{bucket}/{output_key}")

        return {
            'statusCode': 200,
            'body': f"Processamento concluído para {key}"
        }

    except Exception as e:
        logger.error(f"Erro ao processar arquivo {key}: {e}")
        raise e
