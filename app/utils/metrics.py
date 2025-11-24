import json
import sys
import datetime
from typing import Dict, Any, Optional

def log_metric(
    name: str,
    value: float,
    unit: str = "Count",
    dimensions: Optional[Dict[str, str]] = None,
    namespace: str = "Smart Stock"
):
    """
    Loga uma métrica no formato JSON.
    Pode ser usado com CloudWatch Logs Metric Filters ou EMF (Embedded Metric Format).
    
    Args:
        name: Nome da métrica.
        value: Valor da métrica.
        unit: Unidade (Count, Seconds, Milliseconds, Bytes, etc.).
        dimensions: Dicionário de dimensões (ex: {"Service": "API"}).
        namespace: Namespace da métrica.
    """
    metric_data = {
        "_aws": {
            "Timestamp": int(datetime.datetime.now().timestamp() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": namespace,
                    "Dimensions": [list(dimensions.keys())] if dimensions else [],
                    "Metrics": [{"Name": name, "Unit": unit}]
                }
            ]
        },
        name: value
    }

    if dimensions:
        metric_data.update(dimensions)

    # Para simplificar no MVP, vamos apenas imprimir um JSON estruturado
    # que pode ser ingerido por ferramentas de log.
    # Se quiséssemos EMF real, precisaríamos garantir o formato exato da AWS.
    
    simple_metric = {
        "metric_name": name,
        "metric_value": value,
        "metric_unit": unit,
        "dimensions": dimensions or {},
        "namespace": namespace,
        "type": "metric"
    }
    
    print(json.dumps(simple_metric))
