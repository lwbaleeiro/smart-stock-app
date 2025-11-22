import io
import os
from unittest.mock import patch

# --- Configuração do Ambiente de Teste ---
# Usa um banco de dados SQLite em memória compartilhado entre threads
os.environ['DATABASE_URL'] = "sqlite:///file:memdb1?mode=memory&cache=shared&uri=true"

from fastapi.testclient import TestClient
from app.api.main import app

# --- Dados de Exemplo ---
PRODUCTS_CSV = "produto_id,produto_nome,produto_codigo,produto_preco,produto_estoque_atual\n101,Caneta,PRD101,1.50,100.0"
SALES_CSV = (
    "produto_id,produto_nome,valor_unitario,valor_total_pedido,quantidade,situacao,data_pedido\n"
    + "\n".join([f"101,Caneta,1.50,15.00,{10 + i},Entregue,{i:02d}/10/2023" for i in range(1, 21)])
)

def test_full_pipeline_and_get_prediction():
    with TestClient(app) as client:
        # 1. Fazer o upload para acionar o pipeline
        with patch('app.api.routes.upload.upload_fileobj_to_s3', return_value=True):
            response_upload = client.post(
                "/upload",
                files={
                    "products_file": ("products.csv", io.BytesIO(PRODUCTS_CSV.encode('utf-8')), "text/csv"),
                    "sales_file": ("sales.csv", io.BytesIO(SALES_CSV.encode('utf-8')), "text/csv"),
                }
            )
            assert response_upload.status_code == 200
            assert "processamento foi iniciado" in response_upload.json()["message"]

        # 2. Buscar a previsão gerada no banco de dados
        response_get = client.get("/predictions/101")
        assert response_get.status_code == 200
        prediction_data = response_get.json()
        assert isinstance(prediction_data, list)
        assert len(prediction_data) > 90
        assert "yhat" in prediction_data[0]

def test_get_prediction_not_found():
    with TestClient(app) as client:
        response = client.get("/predictions/999")
        assert response.status_code == 404

def test_upload_invalid_product_file():
    with TestClient(app) as client:
        response = client.post(
            "/upload",
            files={
                "products_file": ("products.csv", io.BytesIO(b"produto_id,produto_nome\n1,Caneta"), "text/csv"),
                "sales_file": ("sales.csv", io.BytesIO(SALES_CSV.encode('utf-8')), "text/csv"),
            }
        )
        assert response.status_code == 400

def test_upload_s3_failure():
    with TestClient(app) as client:
        with patch('app.api.routes.upload.upload_fileobj_to_s3', return_value=False):
            response = client.post(
                "/upload",
                files={
                    "products_file": ("products.csv", io.BytesIO(PRODUCTS_CSV.encode('utf-8')), "text/csv"),
                    "sales_file": ("sales.csv", io.BytesIO(SALES_CSV.encode('utf-8')), "text/csv"),
                }
            )
            assert response.status_code == 500
