"""Configuración y fixtures compartidos para la suite de pruebas de docx_to_markdown."""

import base64
import io
import zipfile
from pathlib import Path
import pytest
import docx

TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QD"
    "wADhgGAWjR9awAAAABJRU5ErkJggg=="
)


@pytest.fixture
def sample_docx_fixture(tmp_path: Path) -> Path:  # pylint: disable=too-many-locals
    """Genera un archivo DOCX de prueba completo con títulos, listas, tablas y formatos."""
    doc = docx.Document()

    # Título principal
    doc.add_heading("Título Principal del Documento", level=1)

    # Párrafo con texto enriquecido
    p1 = doc.add_paragraph()
    p1.add_run("Texto normal con ")
    r_bold = p1.add_run("negrita")
    r_bold.bold = True
    p1.add_run(", ")
    r_italic = p1.add_run("cursiva")
    r_italic.italic = True
    p1.add_run(" y código ")
    r_code = p1.add_run("variable_ejemplo")
    r_code.font.name = "Consolas"
    p1.add_run(". Caracteres especiales: ñ, á, é, í, ó, ú, ü, ¿?")

    # Subtítulo H2
    doc.add_heading("Subsección de Metodología", level=2)

    # Elementos de lista
    doc.add_paragraph("Primer elemento con viñeta", style="List Bullet")
    doc.add_paragraph("Segundo elemento con viñeta", style="List Bullet")

    doc.add_paragraph("Paso 1 numerado", style="List Number")
    doc.add_paragraph("Paso 2 numerado", style="List Number")

    # Tabla con datos, pipes y multilínea
    table = doc.add_table(rows=3, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Cabecera Col 1"
    hdr_cells[1].text = "Cabecera Col 2"

    row1_cells = table.rows[1].cells
    row1_cells[0].text = "Dato 1 | con pipe"
    row1_cells[1].text = "Línea 1\nLínea 2"

    row2_cells = table.rows[2].cells
    row2_cells[0].text = "Dato 2"
    row2_cells[1].text = "Dato final"

    file_path = tmp_path / "test_sample.docx"
    doc.save(str(file_path))
    return file_path


@pytest.fixture
def docx_with_image_fixture(tmp_path: Path) -> Path:
    """Genera un DOCX que contiene una imagen PNG válida incrustada."""
    doc = docx.Document()
    doc.add_heading("Documento con Imagen", level=1)
    doc.add_paragraph("A continuación una imagen:")
    img_data = base64.b64decode(TINY_PNG_B64)
    doc.add_picture(io.BytesIO(img_data))
    file_path = tmp_path / "test_image.docx"
    doc.save(str(file_path))
    return file_path


@pytest.fixture
def corrupted_docx_fixture(tmp_path: Path) -> Path:
    """Genera un archivo de texto plano con extensión .docx."""
    bad_file = tmp_path / "corrupted.docx"
    bad_file.write_text("Este no es un archivo ZIP ni DOCX", encoding="utf-8")
    return bad_file


@pytest.fixture
def non_docx_zip_fixture(tmp_path: Path) -> Path:
    """Genera un archivo ZIP válido que no es un contenedor OOXML."""
    zip_path = tmp_path / "fake.docx"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("test.txt", "Hola mundo sin OOXML")
    return zip_path
