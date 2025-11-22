import pandas as pd
from typing import Dict
from app.ml.prophet_model import ProphetModel

def train_models_for_products(
    product_dfs: Dict[str, pd.DataFrame]
) -> Dict[str, ProphetModel]:
    """
    Treina um modelo Prophet para cada produto.

    Args:
        product_dfs: Um dicionário de DataFrames formatados para o Prophet,
                     onde cada chave é um ID de produto.

    Returns:
        Um dicionário onde as chaves são os IDs dos produtos e os valores
        são as instâncias dos modelos Prophet treinados.
    """
    trained_models = {}
    for product_id, df in product_dfs.items():
        # Ignorar produtos com poucos dados para um treino estável
        if len(df) < 10:
            print(f"Produto {product_id} tem dados insuficientes para o treino. Pulando.")
            continue

        print(f"Treinando modelo para o produto {product_id}...")
        model = ProphetModel(
            seasonality_mode='multiplicative',
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True
        )
        model.train(df)
        trained_models[product_id] = model
        print(f"Modelo para o produto {product_id} treinado com sucesso.")

    # TODO: Em uma aplicação real, os modelos treinados devem ser serializados
    # (ex: com pickle ou joblib) e salvos em um local persistente, como o S3.
    # Ex: save_model_to_s3(model, bucket, f"models/{product_id}.pkl")

    return trained_models
