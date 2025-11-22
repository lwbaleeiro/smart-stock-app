import pandas as pd
from prophet import Prophet

class ProphetModel:
    """
    Um wrapper para o modelo Prophet da Meta.
    """
    def __init__(self, **kwargs):
        """
        Inicializa o modelo Prophet.

        Args:
            **kwargs: Argumentos para passar para o construtor do Prophet
                      (ex: seasonality_mode, daily_seasonality, etc.).
        """
        self.model = Prophet(**kwargs)

    def train(self, df: pd.DataFrame):
        """
        Treina o modelo com o DataFrame fornecido.

        Args:
            df: DataFrame contendo as colunas 'ds' e 'y'.
        """
        if 'ds' not in df.columns or 'y' not in df.columns:
            raise ValueError("O DataFrame de treino deve conter as colunas 'ds' e 'y'.")

        self.model.fit(df)

    def predict(self, days: int) -> pd.DataFrame:
        """
        Gera uma previsão para um número de dias no futuro.

        Args:
            days: O número de dias a prever no futuro.

        Returns:
            Um DataFrame contendo a previsão.
        """
        future = self.model.make_future_dataframe(periods=days)
        forecast = self.model.predict(future)
        return forecast
