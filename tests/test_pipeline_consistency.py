import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from app.api.routes.upload import run_ml_pipeline_task

@patch('app.api.routes.upload.SessionLocal')
@patch('app.api.routes.upload.save_products_to_db')
@patch('app.api.routes.upload.create_prophet_features')
@patch('app.api.routes.upload.train_models_for_products')
@patch('app.api.routes.upload.generate_predictions')
@patch('app.api.routes.upload.save_predictions_to_db')
def test_run_ml_pipeline_task_filters_missing_products(
    mock_save_predictions,
    mock_generate_predictions,
    mock_train_models,
    mock_create_features,
    mock_save_products,
    mock_session_local
):
    # Setup mocks
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    
    # Products DF has only product 1
    products_df = pd.DataFrame({
        'produto_id': [1],
        'produto_nome': ['Prod 1'],
        'produto_codigo': ['P1'],
        'produto_preco': [10.0],
        'produto_estoque_atual': [100]
    })
    
    # Sales DF has product 1 AND product 2 (which is missing from products)
    sales_df = pd.DataFrame({
        'produto_id': [1, 2],
        'data_pedido': pd.to_datetime(['2023-01-01', '2023-01-01']),
        'quantidade': [1, 1],
        'valor_total_pedido': [10.0, 20.0]
    })
    
    # Mock feature engineering to return features for whatever is passed
    def side_effect_create_features(df):
        # Return a dict of dfs, one per product in the input df
        return {pid: df[df['produto_id'] == pid] for pid in df['produto_id'].unique()}
    mock_create_features.side_effect = side_effect_create_features
    
    # Mock training to return a model for each feature df
    mock_train_models.return_value = {1: MagicMock(), 2: MagicMock()}
    
    # Mock predictions
    mock_generate_predictions.return_value = {1: pd.DataFrame(), 2: pd.DataFrame()}
    
    # Run the pipeline
    run_ml_pipeline_task(products_df, sales_df)
    
    # Verification
    # save_products_to_db should be called
    mock_save_products.assert_called_once()
    
    # CRITICAL: create_prophet_features should ONLY receive data for product 1
    # If it receives data for product 2, then we haven't filtered correctly
    args, _ = mock_create_features.call_args
    passed_sales_df = args[0]
    
    # This assertion will FAIL before the fix, and PASS after the fix
    assert 2 not in passed_sales_df['produto_id'].values, "Product 2 should have been filtered out"
    assert 1 in passed_sales_df['produto_id'].values
