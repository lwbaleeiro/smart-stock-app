import sys
import os
import pandas as pd
import io

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.processing.validator import validate_csv, PRODUCT_COLUMNS
from app.processing.cleaner import clean_products_data

def test_product_csv_processing():
    csv_path = "docs/products.csv"
    print(f"Testing with file: {csv_path}")
    
    with open(csv_path, "rb") as f:
        # 1. Validate CSV
        is_valid, message = validate_csv(f, PRODUCT_COLUMNS)
        print(f"Validation result: {is_valid}, Message: {message}")
        
        if not is_valid:
            print("FAILED: Validation failed.")
            return

        # Reset pointer for cleaning
        f.seek(0)
        
        # 2. Clean Data
        try:
            df = clean_products_data(f)
            print("Cleaning successful.")
            print("Columns:", df.columns.tolist())
            print("Head:\n", df.head())
            
            expected_cols = ['produto_id', 'produto_nome', 'produto_codigo', 'produto_preco']
            if all(col in df.columns for col in expected_cols):
                 print("PASSED: All expected columns are present.")
            else:
                 print(f"FAILED: Missing columns. Expected {expected_cols}, got {df.columns.tolist()}")

        except Exception as e:
            print(f"FAILED: Cleaning raised exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_product_csv_processing()
