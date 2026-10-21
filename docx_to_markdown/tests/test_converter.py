"""Pruebas de integración del orquestador DocxConverter y cumplimiento de especificación."""

import hashlib
import json
from pathlib import Path

from docx_to_markdown.converter import DocxConverter
from docx_to_markdown.models import ConversionConfig


def test_converter_sample_document(sample_docx_fixture: Path, tmp_path: Path) -> None:
    """Valida la conversión completa de un DOCX a Markdown y emisión de manifiesto."""
    out_md = tmp_path / "output.md"
    orig_mtime = sample_docx_fixture.stat().st_mtime
    orig_hash = hashlib.sha256(sample_docx_fixture.read_bytes()).hexdigest()

    converter = DocxConverter()
    result = converter.convert(sample_docx_fixture, out_md)

    # 1. Verificación del resultado
    assert result.success is True
    assert result.duration_ms > 0
    assert out_md.exists()

    # 2. Inmutabilidad estricta del archivo fuente
    assert sample_docx_fixture.stat().st_mtime == orig_mtime
    assert hashlib.sha256(sample_docx_fixture.read_bytes()).hexdigest() == orig_hash

    # 3. Verificación de contenido Markdown
    content = out_md.read_text(encoding="utf-8")
    assert "# Título Principal del Documento" in content
    assert "**negrita**" in content
    assert "*cursiva*" in content
    assert "`variable_ejemplo`" in content
    assert "## Subsección de Metodología" in content
    assert "- Primer elemento con viñeta" in content
    assert "1. Paso 1 numerado" in content
    assert "| Cabecera Col 1 | Cabecera Col 2 |" in content
    assert r"Dato 1 \| con pipe" in content
    assert "Línea 1<br>Línea 2" in content
    assert "ñ, á, é, í, ó, ú, ü, ¿?" in content

    # 4. Verificación del manifiesto
    manifest_path = tmp_path / "conversion_manifest.json"
    assert manifest_path.exists()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_data["status"] == "SUCCESS"
    assert manifest_data["elements_detected"]["headings_by_level"]["1"] == 1
    assert manifest_data["elements_detected"]["headings_by_level"]["2"] == 1
    assert manifest_data["elements_detected"]["tables"] == 1


def test_converter_with_images(docx_with_image_fixture: Path, tmp_path: Path) -> None:
    """Valida la extracción física de imágenes a assets/ y checksums."""
    out_md = tmp_path / "doc_with_img.md"
    converter = DocxConverter(config=ConversionConfig(extract_images=True))
    result = converter.convert(docx_with_image_fixture, out_md)

    assert result.success is True
    assert result.stats.images == 1

    assets_dir = tmp_path / "assets"
    assert assets_dir.exists()
    extracted_images = list(assets_dir.glob("img_*.*"))
    assert len(extracted_images) == 1

    content = out_md.read_text(encoding="utf-8")
    assert "](assets/img_001.png)" in content


def test_converter_real_document(tmp_path: Path) -> None:
    """Valida la conversión del documento de tesis real disponible en el repositorio."""
    real_docx = Path("docs/SDLC-AI_Tesis_Entrega1.docx")
    if not real_docx.exists():
        return

    out_md = tmp_path / "tesis_convertida.md"
    converter = DocxConverter()
    result = converter.convert(real_docx, out_md)

    assert result.success is True
    assert out_md.exists()
    content = out_md.read_text(encoding="utf-8")
    assert "# RESUMEN" in content
    assert "# CAPÍTULO 1: INTRODUCCIÓN" in content
    assert result.stats.tables >= 1
