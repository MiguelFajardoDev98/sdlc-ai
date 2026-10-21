# TECHNICAL DESIGN DOCUMENT (TDD) — SPRINT 2: MOTOR DE ALERTAS

- **Autor:** Agente Arquitecto (`Architect_Agent`)
- **Fase SDLC:** Fase B — Diseño Técnico

---

## 1. ESTRUCTURAS DE DATOS

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict

class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    OPPORTUNITY = "OPPORTUNITY"

class AlertType(str, Enum):
    CRITICAL_STOCKOUT = "CRITICAL_STOCKOUT"
    WARNING_LOW_STOCK = "WARNING_LOW_STOCK"
    OVERSTOCK_RISK = "OVERSTOCK_RISK"
    HEALTHY = "HEALTHY"
    TRANSFER_OPPORTUNITY = "TRANSFER_OPPORTUNITY"

@dataclass
class Alert:
    alert_type: AlertType
    severity: AlertSeverity
    sku: str
    tienda_id: str
    mensaje: str
    dci: float
    stock_actual: int
    tienda_destino: Optional[str] = None
    unidades_sugeridas: Optional[int] = None
```

## 2. COMPONENTES DEL MOTOR (`src/alert_engine.py`)
- `AlertEngine`: Clase principal con lógica de evaluación de stock por tienda y correlación multitienda para redistribución.
- Cálculo de matriz de confusión y cómputo de métricas `precision`, `recall` y `f1_score`.
