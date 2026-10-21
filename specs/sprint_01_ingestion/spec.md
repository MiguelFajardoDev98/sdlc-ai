# ESPECIFICACIÓN DE REQUISITOS (SRS) — SPRINT 1: INGESTA Y KPIS

- **Sprint:** 01 — Ingesta de Datos y Cálculo de KPIs Logísticos
- **Dominio:** Retail de Moda en Colombia
- **Formato de SKU Obligatorio:** `MODELO-TALLA-COLOR`
- **Sintaxis de Requisitos:** EARS (Easy Approach to Requirements Syntax)

---

## 1. REQUISITOS DEL SISTEMA (EARS)

### REQ-01 (Ubiquitous): Formato Estricto de SKU
El sistema **deberá** validar que cada identificador de producto cumpla la sintaxis `[MODELO]-[TALLA]-[COLOR]`, donde:
- `MODELO`: Cadena alfanumérica en mayúsculas (`^[A-Z0-9_]+$`).
- `TALLA`: Talla estándar alfanumérica (`^[A-Z0-9]+$`).
- `COLOR`: Nombre del color en mayúsculas (`^[A-Z0-9]+$`).

### REQ-02 (Event-Driven): Ingesta y Limpieza de Datos
**Cuando** se ingeste un archivo de inventario (CSV o JSON), el sistema **deberá** validar la existencia de las columnas obligatorias (`sku`, `modelo`, `talla`, `color`, `tienda_id`, `stock_actual`, `ventas_ultimos_30d`, `precio_unitario`) y descartar filas con valores nulos o stocks negativos, registrando el conteo de filas descartadas.

### REQ-03 (State-Driven): Cómputo de Días de Cobertura de Inventario (DCI)
**Mientras** el sistema procese un SKU con ventas positivas ($\text{ventas\_30d} > 0$), el sistema **deberá** calcular los días de cobertura como:
$$\text{DCI} = \frac{\text{stock\_actual}}{\text{ventas\_30d} / 30{,}0}$$

### REQ-04 (Unwanted Behaviour): Manejo de Venta Cero y Casos de Borde
**Si** un SKU presenta $\text{ventas\_30d} = 0$ y $\text{stock\_actual} > 0$, el sistema **deberá** asignar $\text{DCI} = 999{,}0$ indicando cobertura infinita / sin rotación, previniendo excepciones de división por cero.
**Si** tanto $\text{stock\_actual} = 0$ como $\text{ventas\_30d} = 0$, el sistema **deberá** asignar $\text{DCI} = 0{,}0$.

### REQ-05 (Optional Feature): Métricas Agregadas por Tienda y Modelo
El sistema **deberá** proporcionar métodos para agregar la Tasa de Quiebre de Stock ($TQS$) y el inventario valorizado total a nivel de tienda y categoría.

---

## 2. CRITERIOS DE ACEPTACIÓN
1. `GIVEN` un CSV con 450 registros válidos en formato `MODELO-TALLA-COLOR`, `WHEN` se ejecuta la ingesta, `THEN` se retornan 450 registros tipados y cero errores.
2. `GIVEN` registros con `stock < 0` o formato de SKU corrupto, `WHEN` se ejecuta la validación, `THEN` se rechazan y se aíslan del cálculo de KPIs.
3. Cobertura de pruebas unitarias `>= 80%` y puntaje Pylint `>= 7.0`.
