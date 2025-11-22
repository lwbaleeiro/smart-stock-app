from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PredictionBase(BaseModel):
    ds: datetime
    yhat: float
    yhat_lower: float
    yhat_upper: float

class Prediction(PredictionBase):
    id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)
