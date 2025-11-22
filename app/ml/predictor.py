import pandas as pd
from typing import Dict
from app.ml.prophet_model import ProphetModel

def generate_predictions(
    trained_models: Dict[str, ProphetModel],
    days_to_predict: int
) -> Dict[str, pd.DataFrame]:
    """
    Gera previsões para cada modelo treinado.

    Args:
        trained_models: Dicionário com os modelos Prophet treinados.
        days_to_predict: O número de dias a prever no futuro.

    Returns:
        Um dicionário onde as chaves são os IDs dos produtos e os valores
        são os DataFrames com as previsões.
    """
    predictions = {}
    for product_id, model in trained_models.items():
        print(f"Gerando previsão para o produto {product_id}...")
        forecast_df = model.predict(days=days_to_predict)

        # Selecionar colunas relevantes e garantir que a previsão não seja negativa
        forecast_df = forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        forecast_df['yhat'] = forecast_df['yhat'].clip(lower=0)
        forecast_df['yhat_lower'] = forecast_df['yhat_lower'].clip(lower=0)
        forecast_df['yhat_upper'] = forecast_df['yhat_upper'].clip(lower=0)

        predictions[product_id] = forecast_df
        print(f"Previsão para o produto {product_id} gerada com sucesso.")

    # TODO: Em uma aplicação real, as previsões devem ser salvas em um
    # local persistente, como um banco de dados (PostgreSQL) ou S3 (Parquet).
    # Ex: save_predictions_to_db(product_id, forecast_df)

    return predictions
