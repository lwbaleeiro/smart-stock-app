import io
from fastapi import UploadFile
import pandas as pd
from app.processing.validator import validate_csv, PRODUCT_COLUMNS
from app.processing.cleaner import clean_products_data, clean_sales_data
from app.processing.feature_engineering import create_prophet_features

def test_validate_csv_valid():
    """
    Testa a validação de um CSV com colunas válidas.
    """
    csv_content = "produto_id,produto_nome,produto_codigo,produto_preco\n906774455,Coberta,PRD906774455,31.99"
    file = io.BytesIO(csv_content.encode('utf-8'))
    upload_file = UploadFile(filename="products.csv", file=file)

    is_valid, message = validate_csv(upload_file.file, PRODUCT_COLUMNS)
    assert is_valid is True
    assert message == "CSV válido."

def test_validate_csv_missing_columns():
    """
    Testa a validação de um CSV com colunas faltando.
    """
    csv_content = "produto_id,produto_nome,produto_preco\n906774455,Coberta,31.99"
    file = io.BytesIO(csv_content.encode('utf-8'))
    upload_file = UploadFile(filename="products.csv", file=file)

    is_valid, message = validate_csv(upload_file.file, PRODUCT_COLUMNS)
    assert is_valid is False
    assert "Colunas ausentes" in message
    assert "produto_codigo" in message
    assert "produto_situacao" not in message

def test_validate_csv_invalid_format():
    """
    Testa a validação de um arquivo que não é um CSV válido.
    """
    file_content = "isto não é um csv"
    file = io.BytesIO(file_content.encode('utf-8'))
    upload_file = UploadFile(filename="invalid.txt", file=file)

    is_valid, message = validate_csv(upload_file.file, PRODUCT_COLUMNS)
    assert is_valid is False
    assert "Colunas ausentes no CSV" in message

def test_clean_products_data():
    """
    Testa a função de limpeza de dados de produtos.
    """
    csv_content = (
        "produto_id,produto_nome,produto_codigo,produto_preco\n"
        "1,Caneta,PRD1,1.50\n"
        "2,Lapis,PRD2,0.80\n"
        "1,Caneta,PRD1,1.50\n"  # Duplicata de ID
        ",Caderno,,12.00\n"  # ID nulo
        "4,Borracha,PRD4,invalid\n" # Preço inválido
    )
    file = io.BytesIO(csv_content.encode('utf-8'))
    upload_file = UploadFile(filename="products.csv", file=file)

    cleaned_df = clean_products_data(upload_file.file)

    assert len(cleaned_df) == 2
    assert cleaned_df['produto_id'].tolist() == [1.0, 2.0]
    assert pd.api.types.is_numeric_dtype(cleaned_df['produto_preco'])

def test_clean_sales_data():
    """
    Testa a função de limpeza de dados de vendas.
    """
    csv_content = (
        "produto_id,produto_nome,valor_unitario,valor_total_pedido,quantidade,situacao,data_pedido\n"
        "101,Caneta,1.50,15.00,10,Entregue,01/10/2023\n"
        "102,Caderno,12.00,24.00,2,Cancelado,02/10/2023\n" # Cancelado
        "103,Lapis,0.80,4.00,5,Entregue,03/10/2023\n"
        "104,Borracha,2.00,4.00,2,Entregue,invalid_date\n" # Data inválida
        ",Apontador,3.00,3.00,1,Entregue,04/10/2023\n" # ID nulo
    )
    file = io.BytesIO(csv_content.encode('utf-8'))
    upload_file = UploadFile(filename="sales.csv", file=file)

    cleaned_df = clean_sales_data(upload_file.file)

    assert len(cleaned_df) == 2
    assert cleaned_df['produto_id'].tolist() == [101.0, 103.0]
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df['data_pedido'])
    assert 'Cancelado' not in cleaned_df['situacao'].unique()

def test_create_prophet_features():
    """
    Testa a criação de features para o Prophet.
    """
    data = {
        'produto_id': [101, 101, 102, 101],
        'quantidade': [10, 5, 8, 3],
        'data_pedido': ['01/10/2023', '01/10/2023', '02/10/2023', '03/10/2023']
    }
    sales_df = pd.DataFrame(data)
    sales_df['data_pedido'] = pd.to_datetime(sales_df['data_pedido'], format='%d/%m/%Y')

    feature_dfs = create_prophet_features(sales_df)

    assert len(feature_dfs) == 2
    assert 101 in feature_dfs
    assert 102 in feature_dfs

    df_101 = feature_dfs[101]
    assert all(col in df_101.columns for col in ['ds', 'y'])
    # Verifica se agrupou corretamente as vendas do dia 01/10/2023
    assert df_101[df_101['ds'] == '2023-10-01']['y'].iloc[0] == 15
    assert df_101[df_101['ds'] == '2023-10-03']['y'].iloc[0] == 3
