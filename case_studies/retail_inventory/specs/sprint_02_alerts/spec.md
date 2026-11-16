# ESPECIFICACIÓN DE REQUISITOS (SRS) — SPRINT 2: MOTOR DE ALERTAS

- **Sprint:** 02 — Motor Analítico de Alertas y Redistribución Multitienda
- **Dominio:** Retail de Moda en Colombia
- **Formato de SKU:** `MODELO-TALLA-COLOR`
- **Sintaxis:** EARS (Easy Approach to Requirements Syntax)
- **Puntos de Historia del Sprint:** 13 PH (`HU-04`: 5 PH, `HU-05`: 5 PH, `HU-06`: 3 PH)

| Historia de Usuario | Requisitos EARS | Puntos de Historia (PH) |
|---|---|---:|
| `HU-04`: Clasificación de alertas de inventario según criticidad | `REQ-ALERT-01` | 5 |
| `HU-05`: Sugerencia de traslados de mercancía entre tiendas | `REQ-ALERT-02`, `REQ-ALERT-03` | 5 |
| `HU-06`: Generación del archivo Excel de compras y reposición | `REQ-REPL-01` | 3 |

---

## 1. REQUISITOS DEL MOTOR DE ALERTAS

### REQ-ALERT-01 (State-Driven): Clasificación de Severidad por Cobertura
**Mientras** se evalúen los KPIs de un SKU en una tienda:
- Si $\text{DCI} < 7{,}0$ o $\text{stock\_actual} = 0$ con demanda positiva ($\text{ventas\_30d} > 0$), el sistema **deberá** emitir una alerta `CRITICAL_STOCKOUT` (Severidad: ALTA).
- Si $7{,}0 \le \text{DCI} < 15{,}0$, el sistema **deberá** emitir una alerta `WARNING_LOW_STOCK` (Severidad: MEDIA).
- Si $\text{DCI} > 45{,}0$ o ($\text{stock\_actual} > 20$ y $\text{ventas\_30d} \le 2$), el sistema **deberá** emitir una alerta `OVERSTOCK_RISK` (Severidad: BAJA/COMERCIAL).
- Si $15{,}0 \le \text{DCI} \le 45{,}0$, el sistema **deberá** catalogar el estado como `HEALTHY` (Sin alerta activa).

### REQ-ALERT-02 (Event-Driven): Detección de Oportunidades de Transferencia Intertienda
**Cuando** existan dos tiendas diferentes ($T_A \ne T_B$) donde para el mismo SKU exacto (`MODELO-TALLA-COLOR`), la tienda $T_A$ presente `OVERSTOCK_RISK` y la tienda $T_B$ presente `CRITICAL_STOCKOUT` o `WARNING_LOW_STOCK`, el sistema **deberá** generar una recomendación `TRANSFER_OPPORTUNITY` especificando SKU, Tienda Origen, Tienda Destino y Cantidad Sugerida a reasignar.

### REQ-ALERT-03 (Unwanted Behaviour): Prevención de Transferencias No Viables
**Si** la cantidad disponible a transferir desde la tienda de origen no supera el stock de seguridad mínimo (5 unidades), el sistema **no deberá** generar la recomendación de transferencia.

---

## 2. CRITERIOS DE ACEPTACIÓN
1. El motor procesa los 450 ítems del dataset sintético y genera una alerta coherente para cada registro.
2. La precisión analítica evaluada frente al *ground truth* del dataset sintético alcanza un **F1-score $\ge 0{,}80$**.
3. Cobertura de pruebas $\ge 80\%$ y Pylint $\ge 7{,}0$.
