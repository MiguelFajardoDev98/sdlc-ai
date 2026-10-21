# DOCX to Markdown Converter (`docx_to_markdown`)

Módulo modular y reutilizable para la conversión de documentos Microsoft Word (.docx) a Markdown GitHub Flavored (GFM), diseñado e implementado bajo el framework de ciclo de vida agéntico **SDLC-AI**.

---

## 1. Estado del Proyecto en SDLC-AI

- **Task ID:** `sprint_01_conversion`
- **Fase Actual:** **Fase E (Empaquetado, DevOps y Calidad Certificada)**
- **Estado del Pipeline:** `COMPLETED`
- **Artefactos del Sprint:**
  - `specs/sprint_01_conversion/spec_draft.md`: Borrador de especificación.
  - `specs/sprint_01_conversion/audit_report.md`: Dictamen formal de auditoría (`STATUS: APPROVED`).
  - `specs/sprint_01_conversion/spec.md`: Especificación de requisitos inmutable v1.0.
  - `specs/sprint_01_conversion/plan.md`: Documento de Diseño Técnico (TDD).

---

## 2. Métricas y Quality Gates Certificados

| Criterio de Calidad | Umbral Mínimo Requerido | Resultado Obtenido | Estado |
| :--- | :---: | :---: | :---: |
| **Análisis Estático (Pylint)** | $\ge 7.0 / 10.0$ | **10.00 / 10.0** | 🟢 SUPERADO |
| **Cobertura de Pruebas (Pytest-cov)** | $\ge 80\%$ | **95% total** | 🟢 SUPERADO |
| **Pruebas Unitarias e Integración** | $100\%$ pasadas | **18 / 18 pasadas** | 🟢 SUPERADO |
| **Inmutabilidad de Archivo Fuente** | 0 modificaciones / hash idéntico | **Verificado (SHA-256 intacto)** | 🟢 SUPERADO |

---

## 3. Estructura del Directorio

```text
docx_to_markdown/
├── README.md
├── run.sh
├── coverage.json
├── docs/
│   └── SDLC-AI_Tesis_Entrega1_convertida.md
├── specs/
│   └── sprint_01_conversion/
│       ├── spec_draft.md
│       ├── audit_report.md
│       ├── spec.md
│       └── plan.md
├── src/
│   └── docx_to_markdown/
│       ├── __init__.py
│       ├── cli.py
│       ├── converter.py
│       ├── exceptions.py
│       ├── formatter.py
│       ├── models.py
│       └── reader.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_cli.py
    ├── test_converter.py
    ├── test_formatter.py
    └── test_reader.py
```

---

## 4. Uso de la API y CLI

### 4.1 Uso como Biblioteca de Python

```python
from pathlib import Path
from docx_to_markdown import DocxConverter, ConversionConfig

config = ConversionConfig(
    extract_images=True,
    assets_dir_name="assets",
    emit_manifest=True
)

converter = DocxConverter(config=config)
result = converter.convert(
    input_path=Path("documento.docx"),
    output_path=Path("documento.md")
)

print(f"Completado en {result.duration_ms:.2f} ms")
print(f"Párrafos: {result.stats.paragraphs}, Tablas: {result.stats.tables}")
```

### 4.2 Uso desde Línea de Comandos (CLI)

```bash
python -m docx_to_markdown.cli --input documento.docx --output documento.md --extract-images
```

### 4.3 Ejecución de la Suite de Calidad

```bash
./docx_to_markdown/run.sh
```
