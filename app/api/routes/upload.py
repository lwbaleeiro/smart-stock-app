import io
import datetime
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks

from app.processing.validator import validate_csv, PRODUCT_COLUMNS, SALES_COLUMNS
from app.processing.cleaner import clean_products_data, clean_sales_data
from app.processing.feature_engineering import create_prophet_features
from app.ml.trainer import train_models_for_products
from app.ml.predictor import generate_predictions
from app.core.s3 import upload_fileobj_to_s3
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.crud import save_products_to_db, save_predictions_to_db

router = APIRouter()

def run_ml_pipeline_task(products_df: pd.DataFrame, sales_df: pd.DataFrame):
    """
    Executa o pipeline de ML completo e salva os resultados no banco de dados.
    """
    print("Iniciando pipeline de ML...", flush=True)
    try:
        db = SessionLocal()
        try:
            save_products_to_db(db, products_df)
            feature_dfs = create_prophet_features(sales_df)
            trained_models = train_models_for_products(feature_dfs)
            predictions = generate_predictions(trained_models, days_to_predict=90)
            for product_id, forecast_df in predictions.items():
                save_predictions_to_db(db, int(product_id), forecast_df)
            print("Pipeline de ML concluído.", flush=True)
        finally:
            db.close()
    except Exception as e:
        print(f"Erro fatal no pipeline de ML: {e}", flush=True)
        import traceback
        traceback.print_exc()


@router.post("")
async def upload_csv_files(
    background_tasks: BackgroundTasks,
    products_file: UploadFile = File(..., description="CSV de produtos"),
    sales_file: UploadFile = File(..., description="CSV de vendas"),
):
    # (Validação e upload para S3)
    is_valid, message = validate_csv(products_file.file, PRODUCT_COLUMNS)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Arquivo de produtos inválido: {message}")
    is_valid, message = validate_csv(sales_file.file, SALES_COLUMNS)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Arquivo de vendas inválido: {message}")

    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S")
    raw_products_path = f"raw/products_{timestamp}.csv"
    raw_sales_path = f"raw/sales_{timestamp}.csv"
    if not upload_fileobj_to_s3(products_file.file, settings.S3_BUCKET_NAME, raw_products_path):
        raise HTTPException(status_code=500, detail="Upload do arquivo bruto de produtos falhou.")
    if not upload_fileobj_to_s3(sales_file.file, settings.S3_BUCKET_NAME, raw_sales_path):
        raise HTTPException(status_code=500, detail="Upload do arquivo bruto de vendas falhou.")

    # Resetar ponteiros após upload
    products_file.file.seek(0)
    sales_file.file.seek(0)

    products_df = clean_products_data(products_file.file)
    sales_df = clean_sales_data(sales_file.file)

    with io.BytesIO() as buffer:
        products_df.to_parquet(buffer, index=False)
        buffer.seek(0)
        processed_products_path = f"processed/products_{timestamp}.parquet"
        if not upload_fileobj_to_s3(buffer, settings.S3_BUCKET_NAME, processed_products_path):
            raise HTTPException(status_code=500, detail="Upload do arquivo processado de produtos falhou.")

    with io.BytesIO() as buffer:
        sales_df.to_parquet(buffer, index=False)
        buffer.seek(0)
        processed_sales_path = f"processed/sales_{timestamp}.parquet"
        if not upload_fileobj_to_s3(buffer, settings.S3_BUCKET_NAME, processed_sales_path):
            raise HTTPException(status_code=500, detail="Upload do arquivo processado de vendas falhou.")

    # Agendar o pipeline de ML
    background_tasks.add_task(run_ml_pipeline_task, products_df, sales_df)

    return {
        "message": "Arquivos recebidos. O processamento foi iniciado.",
        "raw_files": [raw_products_path, raw_sales_path],
        "processed_files": [processed_products_path, processed_sales_path],
    }
