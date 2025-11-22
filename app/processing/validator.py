import pandas as pd
import io
from typing import List, Tuple, BinaryIO

def validate_csv(file_obj: BinaryIO, expected_columns: List[str]) -> Tuple[bool, str]:
    """
    Valida um arquivo CSV com base nas colunas esperadas.

    Args:
        file_obj: O arquivo CSV enviado (file-like object).
        expected_columns: Uma lista de nomes de colunas que o CSV deve conter.

    Returns:
        Uma tupla contendo:
        - bool: True se o CSV for válido, False caso contrário.
        - str: Uma mensagem de erro ou sucesso.
    """
    try:
        # Ler o conteúdo para memória para evitar que o pandas feche o arquivo original
        content = file_obj.read()
        file_obj.seek(0) # Resetar o ponteiro do arquivo original
        
        # Criar um BytesIO com o conteúdo
        buffer = io.BytesIO(content)
        
        df = pd.read_csv(buffer)

        if not all(col in df.columns for col in expected_columns):
            missing_cols = [col for col in expected_columns if col not in df.columns]
            return False, f"Colunas ausentes no CSV: {', '.join(missing_cols)}"

        return True, "CSV válido."

    except Exception as e:
        return False, f"Erro ao processar o arquivo CSV: {e}"

# Definindo as colunas esperadas para cada tipo de arquivo
PRODUCT_COLUMNS = [
    "produto_id", "produto_nome", "produto_codigo", "produto_preco", "produto_estoque_atual"
]

SALES_COLUMNS = [
    "produto_id", "produto_nome", "valor_unitario", "valor_total_pedido",
    "quantidade", "situacao", "data_pedido"
]
