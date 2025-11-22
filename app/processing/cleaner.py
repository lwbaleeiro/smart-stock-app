import pandas as pd
from typing import BinaryIO

import io

def clean_products_data(file_obj: BinaryIO) -> pd.DataFrame:
    """
    Lê e limpa os dados de produtos de um arquivo CSV.

    - Converte 'produto_preco' para tipo numérico.
    - Remove produtos com 'produto_id' duplicado, mantendo o primeiro.
    - Remove linhas onde 'produto_id' ou 'produto_nome' são nulos.

    Args:
        file_obj: O objeto de arquivo CSV de produtos (file-like object).

    Returns:
        Um DataFrame do Pandas com os dados limpos.
    """
    # Ler conteúdo para memória
    content = file_obj.read()
    file_obj.seek(0)
    buffer = io.BytesIO(content)
    
    df = pd.read_csv(buffer)

    # Corrigir tipos de dados
    df['produto_preco'] = pd.to_numeric(df['produto_preco'], errors='coerce')
    df['produto_estoque_atual'] = pd.to_numeric(df['produto_estoque_atual'], errors='coerce')

    # Remover nulos em colunas críticas
    # Remover nulos em colunas críticas
    df.dropna(subset=['produto_id', 'produto_nome', 'produto_preco'], inplace=True)

    # Remover duplicatas
    # Remover duplicatas
    df.drop_duplicates(subset=['produto_id'], keep='first', inplace=True)

    return df

def clean_sales_data(file_obj: BinaryIO) -> pd.DataFrame:
    """
    Lê e limpa os dados de vendas de um arquivo CSV.

    - Converte 'data_pedido' para datetime.
    - Converte colunas de valor e quantidade para tipos numéricos.
    - Remove vendas com situação 'Cancelado'.
    - Remove linhas onde colunas críticas são nulas.

    Args:
        file_obj: O objeto de arquivo CSV de vendas (file-like object).

    Returns:
        Um DataFrame do Pandas com os dados limpos.
    """
    # Ler conteúdo para memória
    content = file_obj.read()
    file_obj.seek(0)
    buffer = io.BytesIO(content)

    df = pd.read_csv(buffer)

    # Corrigir tipos de dados
    df['data_pedido'] = pd.to_datetime(df['data_pedido'], format='%d/%m/%Y', errors='coerce')
    numeric_cols = ['valor_unitario', 'valor_total_pedido', 'quantidade']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remover vendas canceladas
    df = df[df['situacao'].str.lower() != 'cancelado']

    # Remover nulos em colunas críticas
    df.dropna(subset=['produto_id', 'data_pedido', 'quantidade'], inplace=True)

    return df
