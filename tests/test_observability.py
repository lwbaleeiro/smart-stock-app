from app.utils.logger import logger
from app.utils.metrics import log_metric
import json

def test_logger():
    print("\n--- Testing Logger ---")
    logger.info("Teste de log de info", extra={"extra_fields": {"user_id": "123"}})
    logger.error("Teste de log de erro", exc_info=True)

def test_metrics():
    print("\n--- Testing Metrics ---")
    log_metric("ProcessedFiles", 1, unit="Count", dimensions={"FileType": "CSV"})
    log_metric("ProcessingTime", 150.5, unit="Milliseconds")

if __name__ == "__main__":
    test_logger()
    test_metrics()
