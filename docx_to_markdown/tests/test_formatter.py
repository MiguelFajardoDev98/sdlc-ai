"""Pruebas unitarias para el formateador MarkdownFormatter."""

from docx_to_markdown.formatter import MarkdownFormatter
from docx_to_markdown.models import (
    ConversionConfig,
    DocumentElement,
    ElementType,
    ExtractedImage,
)


def test_format_heading_levels() -> None:
    """Verifica la generación de encabezados de nivel 1 a 6 y acotamiento."""
    formatter = MarkdownFormatter(ConversionConfig())
    assert formatter.format_heading("H1", 1) == "# H1"
    assert formatter.format_heading("H3", 3) == "### H3"
    assert formatter.format_heading("H6", 6) == "###### H6"
    # Acotamiento para valores fuera de rango
    assert formatter.format_heading("H0", 0) == "# H0"
    assert formatter.format_heading("H8", 8) == "###### H8"


def test_format_list_items() -> None:
    """Verifica formateo de listas ordenadas, desordenadas y con indentación."""
    formatter = MarkdownFormatter(ConversionConfig())
    assert formatter.format_list_item("Bullet", 0, is_ordered=False) == "- Bullet"
    assert formatter.format_list_item("Anidado", 1, is_ordered=False) == "  - Anidado"
    assert formatter.format_list_item("Paso", 0, is_ordered=True, index=1) == "1. Paso"
    assert formatter.format_list_item("Paso 2", 0, is_ordered=True, index=2) == "2. Paso 2"


def test_format_table_escaping_and_linebreaks() -> None:
    """Verifica el escape de pipes y el reemplazo de saltos de línea en tablas GFM."""
    formatter = MarkdownFormatter(ConversionConfig(table_cell_linebreak_replacement="<br>"))
    matrix = [
        ["Columna 1", "Columna 2"],
        ["Texto | con pipe", "Línea 1\nLínea 2"],
    ]
    table_md = formatter.format_table(matrix)
    lines = table_md.strip().split("\n")

    assert len(lines) == 3
    assert lines[0] == "| Columna 1 | Columna 2 |"
    assert lines[1] == "| --- | --- |"
    assert r"Texto \| con pipe" in lines[2]
    assert "Línea 1<br>Línea 2" in lines[2]


def test_format_empty_table() -> None:
    """Verifica que una matriz vacía devuelva cadena vacía."""
    formatter = MarkdownFormatter(ConversionConfig())
    assert formatter.format_table([]) == ""
    assert formatter.format_table([[]]) == ""


def test_format_elements_full_flow() -> None:
    """Verifica la conversión integral de una colección de elementos mixtos."""
    formatter = MarkdownFormatter(ConversionConfig())
    elements = [
        DocumentElement(ElementType.HEADING, "Título", level=1),
        DocumentElement(ElementType.PARAGRAPH, "Párrafo explicativo."),
        DocumentElement(ElementType.LIST_ITEM, "Item 1", level=0, metadata={"ordered": True}),
        DocumentElement(ElementType.LIST_ITEM, "Item 2", level=0, metadata={"ordered": True}),
        DocumentElement(
            ElementType.IMAGE,
            ExtractedImage(
                filename="img_001.png",
                data=b"dummy",
                rel_path="assets/img_001.png",
                sha256="abc",
                alt_text="Diagrama",
            ),
        ),
        DocumentElement(ElementType.UNSUPPORTED, "SmartArt", metadata={"type": "SmartArt"}),
    ]

    md_text, warnings, stats = formatter.format_elements(elements)

    assert "# Título" in md_text
    assert "Párrafo explicativo." in md_text
    assert "1. Item 1" in md_text
    assert "2. Item 2" in md_text
    assert "![Diagrama](assets/img_001.png)" in md_text
    assert "<!-- WARNING: Elemento no representable omitido: SmartArt -->" in md_text
    assert len(warnings) == 1
    assert stats.headings_by_level[1] == 1
    assert stats.paragraphs >= 1
    assert stats.images == 1
