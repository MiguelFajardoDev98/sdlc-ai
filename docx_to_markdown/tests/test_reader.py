"""Pruebas unitarias para el lector DocxReader y validación de guardarraíles."""

from pathlib import Path
import pytest

from docx_to_markdown.exceptions import DocumentNotFoundError, InvalidDocxError
from docx_to_markdown.models import ConversionConfig, ElementType
from docx_to_markdown.reader import DocxReader


def test_validate_file_missing(tmp_path: Path) -> None:
    """Verifica que un archivo inexistente lance DocumentNotFoundError."""
    reader = DocxReader()
    missing_file = tmp_path / "inexistente.docx"
    with pytest.raises(DocumentNotFoundError):
        reader.validate_file(missing_file)


def test_validate_file_is_directory(tmp_path: Path) -> None:
    """Verifica que una ruta a directorio lance DocumentNotFoundError."""
    reader = DocxReader()
    with pytest.raises(DocumentNotFoundError):
        reader.validate_file(tmp_path)


def test_validate_file_corrupted(corrupted_docx_fixture: Path) -> None:
    """Verifica que un archivo no ZIP lance InvalidDocxError."""
    reader = DocxReader()
    with pytest.raises(InvalidDocxError):
        reader.validate_file(corrupted_docx_fixture)


def test_validate_file_non_ooxml_zip(non_docx_zip_fixture: Path) -> None:
    """Verifica que un ZIP sin document.xml lance InvalidDocxError."""
    reader = DocxReader()
    with pytest.raises(InvalidDocxError):
        reader.validate_file(non_docx_zip_fixture)


def test_read_sample_document(sample_docx_fixture: Path) -> None:
    """Valida la extracción semántica secuencial del documento de prueba."""
    reader = DocxReader()
    elements = reader.read(sample_docx_fixture)

    assert len(elements) > 0

    types = [el.element_type for el in elements]
    assert ElementType.HEADING in types
    assert ElementType.PARAGRAPH in types
    assert ElementType.LIST_ITEM in types
    assert ElementType.TABLE in types

    # Validar niveles de encabezados
    headings = [el for el in elements if el.element_type == ElementType.HEADING]
    assert headings[0].level == 1
    assert "Título Principal" in headings[0].content
    assert headings[1].level == 2
    assert "Subsección de Metodología" in headings[1].content

    # Validar tabla
    tables = [el for el in elements if el.element_type == ElementType.TABLE]
    assert len(tables) == 1
    table_data = tables[0].content
    assert len(table_data) == 3
    assert table_data[0][0] == "Cabecera Col 1"


def test_read_document_with_image(docx_with_image_fixture: Path) -> None:
    """Valida la detección y extracción de imágenes incrustadas."""
    reader = DocxReader()
    config = ConversionConfig(extract_images=True)
    elements = reader.read(docx_with_image_fixture, config=config)

    images = [el for el in elements if el.element_type == ElementType.IMAGE]
    assert len(images) == 1
    img = images[0].content
    assert img.filename.startswith("img_")
    assert len(img.data) > 0
    assert len(img.sha256) == 64


def test_read_document_ignore_images_when_disabled(docx_with_image_fixture: Path) -> None:
    """Verifica que no se extraigan imágenes si extract_images=False."""
    reader = DocxReader()
    config = ConversionConfig(extract_images=False)
    elements = reader.read(docx_with_image_fixture, config=config)

    images = [el for el in elements if el.element_type == ElementType.IMAGE]
    assert len(images) == 0
