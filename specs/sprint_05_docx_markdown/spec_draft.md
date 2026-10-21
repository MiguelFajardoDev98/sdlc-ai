# ESPECIFICACIÓN DE REQUISITOS DE SOFTWARE (SRS) — CONVERTIDOR DOCX A MARKDOWN

> [!WARNING] DOCUMENTO HISTÓRICO / DUPLICADO
> Este documento se conserva como evidencia histórica. La versión y ruta activa canónica es: [`docx_to_markdown/specs/sprint_01_conversion/spec_draft.md`](file:///home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/docx_to_markdown/specs/sprint_01_conversion/spec_draft.md) bajo el task_id `sprint_01_conversion`.

- **Proyecto:** `docx_to_markdown` (Módulo Extractor y Normalizador de Documentos)
- **Sprint:** 05 — Conversión de DOCX a Markdown con Trazabilidad Estructural
- **Dominio:** Conversión de Documentos Técnicos y Académicos (OOXML Word a Markdown GFM)
- **Skills Activas:** `document_conversion`, `python_architect`
- **Sintaxis de Requisitos:** EARS (Easy Approach to Requirements Syntax)
- **Estado:** DRAFT (Sometido a Auditoría)

---

## 1. OBJETIVO DEL SISTEMA Y ALCANCE

El objetivo del proyecto `docx_to_markdown` es proporcionar una biblioteca y utilidad CLI en Python 3.10+ capaz de ingerir documentos en formato Microsoft Word (.docx), analizar su árbol semántico (Open Packaging Conventions / OOXML) y emitir un documento Markdown normalizado (GitHub Flavored Markdown - GFM) en codificación UTF-8.

El sistema garantiza:
1. **Fidelidad Estructural:** Preservación de jerarquías de encabezados, párrafos, listas ordenadas/desordenadas y tablas bidimensionales con alineaciones.
2. **Extracción Determinista de Medios:** Aislamiento de imágenes y diagramas embebidos en un directorio local de artefactos (`assets/`), referenciándolos con rutas relativas limpias.
3. **Inmutabilidad y No-Alucinación:** Cero modificaciones sobre el archivo DOCX de origen, preservación íntegra del texto original sin resúmenes ni interpolaciones automáticas.
4. **Trazabilidad y Reporte de Discrepancias:** Auditoría cuantitativa de elementos procesados y emisión de advertencias estructuradas ante componentes no mapeables (SmartArt, objetos OLE, macros).

---

## 2. HISTORIAS DE USUARIO (USER STORIES)

### US-01: Extracción Estructural de Texto y Jerarquía
- **Como:** Investigador o Autor de documentos académicos y técnicos.
- **Quiero:** Convertir un archivo DOCX estructurado a Markdown.
- **Para:** Versionar el contenido en repositorios Git y procesarlo mediante herramientas de documentación estática sin perder la estructura de títulos, párrafos y listas.

### US-02: Preservación de Tablas y Formato Enriquecido
- **Como:** Desarrollador o Analista de Datos.
- **Quiero:** Que las tablas complejas y el formato enriquecido (negrita, cursiva, código, enlaces, notas al pie) se traduzcan fielmente a tablas GFM y sintaxis estándar.
- **Para:** Mantener la integridad de datos tabulares, citas y referencias bibliográficas sin reconstrucción manual.

### US-03: Auditoría y Manifiesto de Conversión
- **Como:** Administrador de Calidad del Software (QA / Auditor).
- **Quiero:** Obtener un manifiesto estructurado (`conversion_manifest.json`) con métricas de elementos extraídos y advertencias de elementos no mapeables.
- **Para:** Verificar matemáticamente que no hubo pérdida inadvertida de contenido durante la transformación.

---

## 3. REQUISITOS FUNCIONALES (SINTAXIS EARS)

### REQ-DOCX-01 (Ubiquitous): Preservación de Encabezados y Jerarquía
El sistema **deberá** mapear de forma determinista los estilos estándar de encabezado de Word a niveles de encabezado Markdown:
- `Heading 1` / `Título 1` $\rightarrow$ `# Titular`
- `Heading 2` / `Título 2` $\rightarrow$ `## Titular`
- `Heading 3` / `Título 3` $\rightarrow$ `### Titular`
- `Heading 4` a `Heading 6` $\rightarrow$ `####` a `######`
- Párrafos ordinarios (`Normal`, `Body Text`) $\rightarrow$ Separados por doble salto de línea (`\n\n`), codificados en UTF-8.

### REQ-DOCX-02 (Event-Driven): Procesamiento de Listas Simples y Anidadas
**Cuando** se procese un párrafo cuyo estilo o numeración corresponda a un elemento de lista (`List Bullet`, `List Number`, o w:numPr):
- Si es lista de viñetas, el sistema **deberá** formatearlo con guion (`- `).
- Si es lista numerada, el sistema **deberá** formatearlo secuencialmente (`1. `, `2. `, etc.).
- Si presenta niveles de indentación jerárquica ($L > 0$), el sistema **deberá** prefijar la línea con $2 \times L$ espacios en blanco para mantener el anidamiento válido en GFM.

### REQ-DOCX-03 (Event-Driven): Conversión de Tablas a GFM
**Cuando** se detecte una tabla en el documento:
- El sistema **deberá** interpretar la primera fila como cabecera (generando la línea separadora obligatoria `|---|---|`).
- El sistema **deberá** limpiar los saltos de línea internos en cada celda (reemplazándolos por `<br>` o espacios) para evitar rupturas de sintaxis tabular.
- El sistema **deberá** escapar los caracteres de barra vertical (`|` $\rightarrow$ `\|`) contenidos en el texto de las celdas.
- El sistema **deberá** conservar el número exacto de columnas y filas correspondientes a la estructura de la tabla.

### REQ-DOCX-04 (Event-Driven): Formato Enriquecido Inline y Referencias
**Cuando** se identifiquen fragmentos de texto (*runs*) con propiedades de estilo:
- Negrita (`w:b`) $\rightarrow$ Envolver en `**texto**`.
- Cursiva (`w:i`) $\rightarrow$ Envolver en `*texto*`.
- Código inline (`Consolas`, `Courier New` o estilo de código) $\rightarrow$ Envolver en `` `texto` ``.
- Hipervínculos (`w:hyperlink`) $\rightarrow$ Convertir a `[texto](url)`.
- Notas al pie de página (`Footnotes`) $\rightarrow$ Generar referencia numérica GFM `[^n]` en el texto y el bloque correspondiente al final del documento `[^n]: Texto de la nota`.

### REQ-DOCX-05 (Event-Driven): Extracción de Medios y Gestión de Imágenes
**Cuando** el documento contenga elementos gráficos incrustados (imágenes PNG, JPEG, SVG):
- El sistema **deberá** extraer el flujo binario original de cada imagen y guardarlo en el directorio `<output_dir>/assets/`.
- El sistema **deberá** asignar nombres deterministas con formato `img_{index:03d}.{ext}` (ej. `img_001.png`).
- El sistema **deberá** insertar en el Markdown la referencia relativa `![alt_text](assets/img_001.png)`.
- Si el DOCX contiene título/descripción de la imagen, **deberá** utilizarse como texto alternativo (`alt_text`).

### REQ-DOCX-06 (Unwanted Behaviour): Inmutabilidad del Archivo Fuente y Validación de Entrada
**Si** el archivo de entrada especificado no existe, tiene permisos denegados o no corresponde a un archivo OOXML válido (.docx reconocible como contenedor ZIP):
- El sistema **no deberá** crear archivos parciales de salida.
- El sistema **deberá** lanzar una excepción controlada (`DocumentNotFoundError` o `InvalidDocxError`).
- El sistema **nunca deberá** abrir el archivo original en modo de escritura ni modificar sus atributos o contenido (Modo Solo Lectura estricto).

### REQ-DOCX-07 (Unwanted Behaviour): Detección de Elementos No Mapeables y No-Alucinación
El sistema **no deberá** omitir silenciosamente texto ni inventar o resumir contenido no presente en el DOCX.
**Si** se identifican elementos que Markdown no soporta nativamente (tales como formas vectoriales complejas, diagramas SmartArt, controles ActiveX u objetos OLE):
- El sistema **deberá** registrar una advertencia estructurada indicando tipo de elemento y posición aproximada.
- El sistema **deberá** insertar un marcador de comentario HTML en el Markdown: `<!-- WARNING: Elemento no representable [TIPO] omitido -->`.

### REQ-DOCX-08 (State-Driven): Telemetría, Conteo y Manifiesto de Conversión
**Mientras** finaliza el proceso de transformación:
El sistema **deberá** generar un objeto de salida y un archivo JSON opcional (`conversion_manifest.json`) que contenga:
```json
{
  "source_path": "/ruta/al/documento.docx",
  "output_path": "/ruta/al/documento.md",
  "elements_detected": {
    "paragraphs": 120,
    "headings": { "h1": 3, "h2": 8, "h3": 4 },
    "tables": 2,
    "images": 5,
    "footnotes": 6
  },
  "warnings": [],
  "processing_time_ms": 142.5,
  "status": "SUCCESS"
}
```

### REQ-DOCX-09 (Optional Feature): Interfaz Dual (API Modular y CLI)
El sistema **deberá** proveer:
1. Una API de Python con tipado estricto (PEP 484) consumible mediante:
   ```python
   converter = DocxConverter(config=ConversionConfig(...))
   result = converter.convert(input_path="documento.docx", output_path="documento.md")
   ```
2. Una interfaz de línea de comandos (CLI):
   ```bash
   python -m docx_to_markdown.cli --input documento.docx --output documento.md --extract-images
   ```

---

## 4. CRITERIOS DE ACEPTACIÓN (GHERKIN / GIVEN-WHEN-THEN)

### CA-01: Conversión de Jerarquía Semántica y Párrafos
```gherkin
GIVEN un documento DOCX válido que contiene títulos H1, H2, H3, párrafos de texto y caracteres especiales UTF-8 (tildes, eñes, símbolos)
WHEN el usuario invoca la conversión mediante el método convert()
THEN se genera un archivo Markdown con etiquetas '#', '##' y '###' respetando la jerarquía original
AND los párrafos están delimitados por saltos de línea dobles
AND el archivo resultante se guarda en codificación UTF-8 sin corrupción de caracteres.
```

### CA-02: Conversión Fiel de Tablas a Sintaxis GFM
```gherkin
GIVEN un documento DOCX con una tabla de 4 filas y 3 columnas con saltos de línea en celdas
WHEN se procesa el documento
THEN la salida contiene una tabla formateada en GFM con barra vertical separadora
AND la fila de encabezado incluye la línea delimitadora '|---|---|---|'
AND los saltos de línea internos se reemplazan por '<br>' preservando la integridad de las columnas.
```

### CA-03: Extracción Segura de Imágenes
```gherkin
GIVEN un documento DOCX que contiene 2 imágenes incrustadas en formato PNG
WHEN se ejecuta la conversión con extracción de medios habilitada
THEN se guardan 2 archivos en la carpeta de destino 'assets/img_001.png' y 'assets/img_002.png'
AND el archivo Markdown resultante contiene las referencias relativas correspondientes
AND los checksums SHA-256 de las imágenes extraídas coinciden exactamente con los streams binarios del paquete OOXML.
```

### CA-04: Robustez, Inmutabilidad y Manejo de Errores
```gherkin
GIVEN una ruta a un archivo inexistente o corrupto (ej. un archivo de texto plano renombrado a .docx)
WHEN se solicita la conversión
THEN el sistema captura la condición y arroja DocumentNotFoundError o InvalidDocxError
AND no se escribe ningún archivo residual en el sistema de archivos
AND el archivo fuente permanece intacto.
```

### CA-05: Calidad del Código y Cobertura de Pruebas
```gherkin
GIVEN los módulos que componen el paquete 'docx_to_markdown'
WHEN se ejecutan las suites de verificación estática y pruebas automatizadas
THEN el puntaje de Pylint es mayor o igual a 7.0/10.0
AND la cobertura de pruebas unitarias calculada con Pytest-cov es mayor o igual al 80%.
```

---

## 5. ESPECIFICACIÓN DE TIPOS Y MODELOS DE DATOS (CONTRATO TÉCNICO)

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

@dataclass(frozen=True)
class ConversionConfig:
    """Configuración de parámetros de conversión."""
    extract_images: bool = True
    assets_dir_name: str = "assets"
    table_cell_linebreak_replacement: str = "<br>"
    emit_manifest: bool = True
    ignore_empty_paragraphs: bool = True

@dataclass
class ElementStats:
    """Métricas cuantitativas de elementos parseados."""
    paragraphs: int = 0
    headings_by_level: Dict[int, int] = field(default_factory=dict)
    tables: int = 0
    table_cells: int = 0
    images: int = 0
    footnotes: int = 0

@dataclass
class ConversionResult:
    """Resultado del proceso de conversión y trazabilidad."""
    source_path: Path
    output_path: Path
    stats: ElementStats
    warnings: List[str]
    duration_ms: float
    success: bool
```

---

## 6. LÍMITES Y GUARDARRAÍLES

1. **No sobrescritura del DOCX:** Bajo ninguna circunstancia el convertidor abrirá el archivo en modo `w` o `a`.
2. **Dependencias limpias:** El convertidor se basará en la biblioteca estándar y librerías declaradas en `requirements.txt` (ej. `python-docx`).
3. **Aislamiento I/O:** Las operaciones de lectura y escritura estarán desacopladas mediante inyección de dependencias para permitir pruebas con documentos de fixture o streams en memoria.
