import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, Product, Prediction
from app.core.crud import save_products_to_db, save_predictions_to_db

# --- Configuração do Banco de Dados de Teste ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# --- Testes ---

def test_save_products_to_db(db_session):
    products_data = {
        'produto_id': [1, 2], 'produto_nome': ['Caneta', 'Lapis'],
        'produto_codigo': ['PRD1', 'PRD2'], 'produto_preco': [10.0, 20.0],
        'produto_estoque_atual': [100.0, 50.0]
    }
    products_df = pd.DataFrame(products_data)
    save_products_to_db(db_session, products_df)
    db_products = db_session.query(Product).all()
    assert len(db_products) == 2
    assert db_products[0].id == 1

def test_save_predictions_to_db(db_session):
    product = Product(id=101, name="Caneta Teste")
    db_session.add(product)
    db_session.commit()

    forecast_data = {
        'ds': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'yhat': [10.5, 12.0], 'yhat_lower': [9.0, 11.0], 'yhat_upper': [12.0, 13.0]
    }
    forecast_df = pd.DataFrame(forecast_data)
    save_predictions_to_db(db_session, 101, forecast_df)
    db_predictions = db_session.query(Prediction).filter(Prediction.product_id == 101).all()
    assert len(db_predictions) == 2
    assert db_predictions[0].yhat == 10.5
