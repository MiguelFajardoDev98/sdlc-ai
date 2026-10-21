---
name: document_conversion
description: Convierte documentos DOCX a Markdown preservando estructura, tablas y trazabilidad.
activation: solicitudes para convertir, migrar, extraer o normalizar documentos Word a Markdown.
---

# Document conversion

## Entrada mínima
Ruta del archivo DOCX, ruta de salida, idioma, nivel de fidelidad esperado,
tratamiento de imágenes/tablas y reglas de formato institucional.

## Procedimiento
1. Inspeccionar el DOCX y enumerar títulos, párrafos, listas, tablas, imágenes,
   notas, referencias y encabezados/pies.
2. Definir un mapeo reproducible de estilos Word a Markdown.
3. Convertir sin perder orden, texto, tablas ni referencias; registrar elementos
   que Markdown no represente completamente.
4. Validar que el archivo de salida sea legible, consistente y no contenga
   contenido inventado.
5. Comparar conteos y generar un reporte de advertencias y archivos producidos.

## Guardrails

No sobrescribir el DOCX original, no inventar texto faltante, no eliminar
tablas o referencias silenciosamente y no afirmar equivalencia perfecta cuando
haya elementos no representables. Mantener codificación UTF-8 y rutas
configurables. Si se requiere código, aislar I/O, usar dependencias declaradas
y añadir pruebas con un documento fixture pequeño.

## Salida

`source`, `output`, `style_mapping`, `validation`, `warnings` y `reproduction`.
