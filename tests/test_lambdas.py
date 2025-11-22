import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import io
import json
from lambdas.process_handler.main import handler as process_handler
from lambdas.predict_handler.main import handler as predict_handler

@pytest.fixture
def mock_s3_event():
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "quantyfy-bucket"},
                    "object": {"key": "raw/products_20231120.csv"}
                }
            }
        ]
    }

@patch("lambdas.process_handler.main.s3_client")
def test_process_handler_products(mock_s3, mock_s3_event):
    # Mock S3 get_object
    csv_content = "produto_id,produto_nome,produto_codigo,produto_preco\n1,Produto A,PRD1,10.0"
    mock_s3.get_object.return_value = {
        "Body": io.BytesIO(csv_content.encode("utf-8"))
    }

    # Run handler
    response = process_handler(mock_s3_event, None)

    # Assertions
    assert response["statusCode"] == 200
    mock_s3.upload_fileobj.assert_called_once()
    args, _ = mock_s3.upload_fileobj.call_args
    bucket, key = args[1], args[2]
    assert bucket == "quantyfy-bucket"
    assert key == "processed/products_20231120.parquet"

@patch("lambdas.predict_handler.main.s3_client")
@patch("lambdas.predict_handler.main.SessionLocal")
@patch("lambdas.predict_handler.main.save_products_to_db")
@patch("lambdas.predict_handler.main.save_predictions_to_db")
def test_predict_handler(mock_save_preds, mock_save_prods, mock_db, mock_s3):
    # Event for sales file
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "quantyfy-bucket"},
                    "object": {"key": "processed/sales_20231120.parquet"}
                }
            }
        ]
    }

    # Mock S3 downloads (Sales and Products)
    # Create dummy dataframes
    sales_df = pd.DataFrame({
        "produto_id": [1] * 10,
        "data_pedido": pd.date_range(start="2023-01-01", periods=10, freq="D").astype(str),
        "quantidade": [10] * 10,
        "valor_unitario": [10] * 10,
        "valor_total_pedido": [100] * 10,
        "situacao": ["Concluido"] * 10
    })
    products_df = pd.DataFrame({
        "produto_id": [1],
        "produto_nome": ["Produto A"],
        "produto_codigo": ["PRD1"],
        "produto_preco": [10.0]
    })

    sales_buffer = io.BytesIO()
    sales_df.to_parquet(sales_buffer)
    sales_buffer.seek(0)

    products_buffer = io.BytesIO()
    products_df.to_parquet(products_buffer)
    products_buffer.seek(0)

    # Mock get_object side effects (first call sales, second call products)
    mock_s3.get_object.side_effect = [
        {"Body": sales_buffer},
        {"Body": products_buffer}
    ]

    # Run handler
    response = predict_handler(event, None)

    # Assertions
    assert response["statusCode"] == 200
    assert mock_save_prods.called
    assert mock_save_preds.called
    assert mock_s3.upload_fileobj.called # Should upload forecast
