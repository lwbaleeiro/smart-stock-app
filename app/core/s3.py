import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import UploadFile
from app.core.config import settings
from app.utils.file_utils import NonCloseableFile

def get_s3_client():
    """
    Cria e retorna um cliente S3.
    Suporta credenciais explícitas (local) e IAM Roles (AWS).
    """
    try:
        client_args = {
            "service_name": "s3",
            "region_name": settings.AWS_REGION
        }

        # Apenas passar credenciais se elas foram configuradas (diferente do default)
        # Isso permite que o boto3 use a IAM Role automaticamente no App Runner/Lambda
        if (settings.AWS_ACCESS_KEY_ID and 
            settings.AWS_ACCESS_KEY_ID != "YOUR_AWS_ACCESS_KEY_ID" and
            settings.AWS_SECRET_ACCESS_KEY and 
            settings.AWS_SECRET_ACCESS_KEY != "YOUR_AWS_SECRET_ACCESS_KEY"):
            
            client_args["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            client_args["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            if settings.AWS_SESSION_TOKEN:
                client_args["aws_session_token"] = settings.AWS_SESSION_TOKEN

        s3_client = boto3.client(**client_args)
        return s3_client
    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found. S3 functionality will be disabled.")
        return None

def upload_fileobj_to_s3(file_obj, bucket_name: str, object_name: str) -> bool:
    """
    Faz o upload de um objeto de arquivo para um bucket S3.

    Args:
        file_obj: O objeto de arquivo a ser enviado.
        bucket_name: O nome do bucket S3.
        object_name: O nome do objeto no S3.

    Returns:
        True se o upload for bem-sucedido, False caso contrário.
    """
    s3_client = get_s3_client()
    if not s3_client:
        return False

    # TODO: Implementar a geração completa do caminho do S3:
    # processed/{company-name}/{cnpj}/{ano}/{mes}/features_{date}.parquet

    try:
        # Envolver o arquivo para evitar que o boto3 o feche
        wrapped_file = NonCloseableFile(file_obj)
        s3_client.upload_fileobj(wrapped_file, bucket_name, object_name)
    except Exception as e:
        # Logar o erro em um sistema de logging real
        print(f"Erro ao fazer upload para o S3: {e}")
        return False
    
    return True

    return True
