import pandas as pd
import io
from app.processing.cleaner import clean_sales_data
from fastapi import UploadFile

def test_clean_sales_data_iso_format():
    csv_content = (
        "produto_id,produto_nome,valor_unitario,valor_total_pedido,quantidade,situacao,data_pedido\n"
        "101,Caneta,1.50,15.00,10,Entregue,2025-11-04\n"
    )
    file = io.BytesIO(csv_content.encode('utf-8'))
    upload_file = UploadFile(filename="sales.csv", file=file)

    cleaned_df = clean_sales_data(upload_file.file)

    # This should fail if the bug exists (df will be empty)
    assert len(cleaned_df) == 1
    assert cleaned_df['data_pedido'].iloc[0].year == 2025
    assert cleaned_df['data_pedido'].iloc[0].month == 11
    assert cleaned_df['data_pedido'].iloc[0].day == 4

def test_clean_sales_data_br_format():
    csv_content = (
        "produto_id,produto_nome,valor_unitario,valor_total_pedido,quantidade,situacao,data_pedido\n"
        "101,Caneta,1.50,15.00,10,Entregue,04/11/2025\n"
    )
    file = io.BytesIO(csv_content.encode('utf-8'))
    upload_file = UploadFile(filename="sales.csv", file=file)

    cleaned_df = clean_sales_data(upload_file.file)

    assert len(cleaned_df) == 1
    assert cleaned_df['data_pedido'].iloc[0].year == 2025
    assert cleaned_df['data_pedido'].iloc[0].month == 11
    assert cleaned_df['data_pedido'].iloc[0].day == 4
