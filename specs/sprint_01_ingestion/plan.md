# TECHNICAL DESIGN DOCUMENT (TDD) — SPRINT 1: INGESTA Y KPIS

- **Autor:** Agente Arquitecto (`Architect_Agent`)
- **Basado en:** `specs/sprint_01_ingestion/spec.md` (Aprobado)
- **Fase SDLC:** Fase B — Diseño Técnico

---

## 1. ESQUEMAS DE DATOS Y CONTRATOS (DATACLASSES)

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class InventoryItem:
    sku: str  # Formato MODELO-TALLA-COLOR
    modelo: str
    talla: str
    color: str
    categoria: str
    tienda_id: str
    ciudad: str
    stock_actual: int
    ventas_ultimos_30d: int
    precio_unitario: float

@dataclass
class InventoryKPI:
    sku: str
    tienda_id: str
    dci: float
    venta_diaria_promedio: float
    valor_inventario: float
    estado_rotacion: str
```

## 2. ARQUITECTURA DE MÓDULOS

### Módulo `src/data_ingestion.py`
- `validate_sku(sku: str) -> bool`: Valida patrón regex `^[A-Z0-9_]+-[A-Z0-9]+-[A-Z0-9]+$`.
- `parse_sku(sku: str) -> Tuple[str, str, str]`: Descompone en `(modelo, talla, color)`.
- `load_inventory_csv(filepath: str) -> List[InventoryItem]`: Carga, valida y filtra filas inválidas.

### Módulo `src/kpi_calculator.py`
- `calculate_item_kpi(item: InventoryItem) -> InventoryKPI`: Computa DCI, venta promedio y estado.
- `calculate_store_kpis(items: List[InventoryItem]) -> Dict[str, Any]`: Computa TQS agregada y valor total.
