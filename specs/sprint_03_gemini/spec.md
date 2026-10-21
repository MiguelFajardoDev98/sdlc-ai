# ESPECIFICACIÓN DE REQUISITOS (SRS) — SPRINT 3: INTEGRACIÓN GEMINI PRO

- **Sprint:** 03 — Integración Gemini Pro y Generación Narrativa
- **Dominio:** Retail de Moda en Colombia
- **Formato de SKU:** `MODELO-TALLA-COLOR`
- **Sintaxis:** EARS (Easy Approach to Requirements Syntax)

---

## 1. REQUISITOS DE REPORTERÍA NARRATIVA

### REQ-GEMINI-01 (Event-Driven): Generación de Resumen Ejecutivo
**Cuando** el pipeline analítico finalice la evaluación de inventario, el sistema **deberá** sintetizar un informe ejecutivo en lenguaje natural estructurado, destacando:
- Tasa general de quiebre de stock ($TQS$) y valor monetario en riesgo.
- Top 3 de modelos más vulnerables a quiebre de stock (`MODELO-TALLA-COLOR`).
- Balance global de transferencias recomendadas entre ciudades.

### REQ-GEMINI-02 (State-Driven): Integración con API y Fallback Determinista
**Mientras** la variable `GEMINI_API_KEY` esté configurada, el sistema **deberá** invocar el endpoint de Google Gemini Pro (`models/gemini-1.5-pro` o compatible).
**Si** la clave no está presente o la conexión no está disponible (modo offline/evaluación académica), el sistema **deberá** emplear un generador analítico determinista que conserve la estructura y coherencia del reporte narrativo.

---

## 2. CRITERIOS DE ACEPTACIÓN
1. Generación de reporte completo sin excepciones.
2. Contiene secciones: Diagnóstico General, Quiebres Críticos, Oportunidades de Transferencia y Recomendaciones de Abastecimiento.
3. Cobertura de pruebas $\ge 80\%$ y Pylint $\ge 7{,}0$.
