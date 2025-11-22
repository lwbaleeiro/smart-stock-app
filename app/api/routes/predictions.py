from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db, Prediction as PredictionModel
from app.api.schemas import Prediction as PredictionSchema

router = APIRouter()

@router.get("/{product_id}", response_model=List[PredictionSchema])
def get_prediction_for_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retorna a previsão de demanda para um produto específico a partir do banco de dados.
    """
    predictions = db.query(PredictionModel).filter(PredictionModel.product_id == product_id).all()

    if not predictions:
        raise HTTPException(
            status_code=404,
            detail="Previsão não encontrada para o produto especificado."
        )

    return predictions
