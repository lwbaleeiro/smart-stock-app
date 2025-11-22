import pandas as pd
import tempfile
import io

def test_pandas_closes_file():
    # Create a dummy CSV in a SpooledTemporaryFile
    with tempfile.SpooledTemporaryFile(mode='w+b') as f:
        f.write(b"col1,col2\n1,2\n3,4")
        f.seek(0)
        
        print(f"File closed before read_csv? {f.closed}")
        
        try:
            df = pd.read_csv(f)
            print("read_csv successful")
        except Exception as e:
            print(f"read_csv failed: {e}")
            
        print(f"File closed after read_csv? {f.closed}")
        
        try:
            f.seek(0)
            print("seek(0) successful")
        except ValueError as e:
            print(f"seek(0) failed: {e}")

if __name__ == "__main__":
    test_pandas_closes_file()
