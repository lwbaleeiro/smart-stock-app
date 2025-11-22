import pandas as pd
from sqlalchemy.orm import Session
from app.core.database import Product, Prediction

def save_products_to_db(db: Session, products_df: pd.DataFrame):
    """
    Salva ou atualiza produtos no banco de dados a partir de um DataFrame.
    """
    print("Salvando produtos no banco de dados...")
    for _, row in products_df.iterrows():
        product_id = int(row['produto_id'])
        # Verifica se o produto já existe
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            # Cria um novo produto se não existir
            db_product = Product(
                id=product_id,
                name=row['produto_nome'],
                code=row['produto_codigo'],
                price=row['produto_preco'],
                stock=row['produto_estoque_atual']
            )
            db.add(db_product)
    db.commit()
    print(f"{len(products_df)} produtos salvos/atualizados.")

def save_predictions_to_db(db: Session, product_id: int, forecast_df: pd.DataFrame):
    """
    Salva as previsões de um produto no banco de dados, limpando as antigas.
    """
    # Deleta previsões antigas para este produto
    db.query(Prediction).filter(Prediction.product_id == product_id).delete()

    # Adiciona as novas previsões
    for _, row in forecast_df.iterrows():
        db_prediction = Prediction(
            product_id=product_id,
            ds=row['ds'],
            yhat=row['yhat'],
            yhat_lower=row['yhat_lower'],
            yhat_upper=row['yhat_upper']
        )
        db.add(db_prediction)
    db.commit()
    print(f"Previsões para o produto {product_id} salvas no banco de dados.")
