---
name: retail_strategist
description: Habilidad especializada en analítica de inventarios y logística para retail de moda en Colombia. Modela curvas de rotación, días de cobertura, estacionalidad textil y reglas de abastecimiento multitienda.
---

# HABILIDAD: RETAIL STRATEGIST (MODA COLOMBIA)

Esta habilidad dota a los agentes de heurísticas y reglas de negocio para la gestión de inventarios en el sector moda en Colombia.

## 1. DIMENSIÓN DEL SKU Y JERARQUÍA DE PRODUCTO
En el retail de moda textil y calzado, la unidad mínima de control es el **SKU**:
- Estructura obligatoria: `[MODELO] - [TALLA] - [COLOR]` (ej. `CAMISA_OXFORD-M-AZUL`, `JEAN_SLIM-32-INDIGO`, `VESTIDO_SEDA-S-ROJO`)
- Curva de tallas colombiana estándar (confección):
  - Femenino: XS (10%), S (30%), M (35%), L (20%), XL (5%).
  - Masculino: S (15%), M (40%), L (35%), XL (10%).
- La rotación no es homogénea: los quiebres de stock suelen ocurrir desproporcionadamente en tallas centrales (S y M), provocando pérdida de ventas mientras las tallas extremas generan inventario ocioso.

## 2. INDICADORES CLAVE DE RENDIMIENTO (KPIS LOGÍSTICOS)

### 2.1 Días de Cobertura de Inventario (DCI)
$$\text{DCI} = \frac{\text{Stock Actual}}{\text{Venta Promedio Diaria (últimos 14 o 30 días)}}$$
- **DCI < 7 días:** Quiebre Inminente (Alerta Roja / Crítica).
- **7 <= DCI < 15 días:** Stock Bajo (Alerta Amarilla / Advertencia de Reabastecimiento).
- **15 <= DCI <= 45 días:** Rango Óptimo y Saludable.
- **DCI > 45 días:** Riesgo de Sobrestock / Baja Rotación (Alerta Azul / Sugerencia de Reasignación Comercial).

### 2.2 Tasa de Quiebre de Stock (TQS)
$$\text{TQS} = \left( \frac{\text{Total SKUs con Stock = 0}}{\text{Total SKUs Activos en Catálogo}} \right) \times 100$$
- Umbral objetivo admisible: $\le 5\%$.

### 2.3 Nivel de Servicio (NS)
$$\text{NS} = \left( \frac{\text{Unidades Vendidas}}{\text{Unidades Demandadas}} \right) \times 100$$

## 3. ESTACIONALIDAD DEL SECTOR MODA EN COLOMBIA
Las alertas y sugerencias deben considerar los picos comerciales del calendario retail colombiano:
1. **Día de la Madre (Mayo):** Pico comercial crítico para líneas femeninas y accesorios.
2. **Día del Padre (Junio):** Concentración en vestuario masculino.
3. **Temporada Escolar (Enero - Febrero):** Demanda masiva de uniformes y calzado formal.
4. **Amor y Amistad (Septiembre):** Dinamización de ticket medio y regalos.
5. **Black Friday / Días sin IVA (Noviembre):** Liquidación de inventario de transición.
6. **Temporada Decembrina / Navidad (Diciembre):** Representa hasta el 30-35% de la facturación anual; tiempos de reposición intertiendas deben minimizarse a 24-48 horas.
