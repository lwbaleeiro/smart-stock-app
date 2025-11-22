import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Formatador de logs que gera saída em JSON.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Adicionar campos extras se existirem
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields)

        # Adicionar exceção se houver
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def configure_logger(name: str = "quantyfy", level: str = "INFO"):
    """
    Configura o logger raiz para usar o formato JSON.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar duplicidade de handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger

# Instância padrão
logger = configure_logger()
