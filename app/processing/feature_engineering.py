import pandas as pd
from typing import Dict

def create_prophet_features(sales_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Transforma o DataFrame de vendas em um formato adequado para o Prophet.

    - Agrupa as vendas por dia e por produto para obter a quantidade total.
    - Renomeia as colunas para 'ds' (data) and 'y' (quantidade).
    - Retorna um dicionário de DataFrames, um para cada produto.

    Args:
        sales_df: O DataFrame de vendas limpo.

    Returns:
        Um dicionário onde as chaves são os IDs dos produtos e os valores
        são os DataFrames formatados para o Prophet.
    """
    # Garantir que a coluna de data está no formato correto
    sales_df['data_pedido'] = pd.to_datetime(sales_df['data_pedido'])

    # Agrupar por dia e produto para somar as quantidades
    daily_sales = sales_df.groupby([
        pd.Grouper(key='data_pedido', freq='D'),
        'produto_id'
    ])['quantidade'].sum().reset_index()

    # Renomear colunas para o formato do Prophet
    daily_sales.rename(columns={'data_pedido': 'ds', 'quantidade': 'y'}, inplace=True)

    # Criar um DataFrame separado para cada produto
    product_dfs = {
        product_id: group[['ds', 'y']]
        for product_id, group in daily_sales.groupby('produto_id')
    }

    return product_dfs
