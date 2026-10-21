"""Orquestador principal del proceso de conversión de DOCX a Markdown."""

import json
import time
from pathlib import Path
from typing import Optional, Union

from docx_to_markdown.formatter import MarkdownFormatter
from docx_to_markdown.models import (
    ConversionConfig,
    ConversionResult,
    DocumentElement,
    ElementType,
    ExtractedImage,
)
from docx_to_markdown.reader import DocxReader, IDocumentReader


class DocxConverter:  # pylint: disable=too-few-public-methods
    """Conversor integral de archivos Microsoft Word a Markdown GFM."""

    def __init__(
        self,
        config: Optional[ConversionConfig] = None,
        reader: Optional[IDocumentReader] = None,
        formatter: Optional[MarkdownFormatter] = None,
    ) -> None:
        """Inicializa el conversor con dependencias inyectables.

        Args:
            config: Opciones de configuración y guardarraíles.
            reader: Instancia del lector que implementa IDocumentReader.
            formatter: Instancia de MarkdownFormatter.
        """
        self.config = config or ConversionConfig()
        self.reader = reader or DocxReader()
        self.formatter = formatter or MarkdownFormatter(self.config)

    def _save_images(
        self, elements: list[DocumentElement], base_output_dir: Path
    ) -> None:
        """Escribe las imágenes extraídas en el directorio de assets."""
        if not self.config.extract_images:
            return

        images = [el.content for el in elements if el.element_type == ElementType.IMAGE]
        if not images:
            return

        assets_dir = base_output_dir / self.config.assets_dir_name
        assets_dir.mkdir(parents=True, exist_ok=True)

        for img in images:
            if isinstance(img, ExtractedImage):
                dest_file = assets_dir / img.filename
                dest_file.write_bytes(img.data)

    def _write_manifest(
        self, manifest_path: Path, result: ConversionResult
    ) -> None:
        """Emite el manifiesto estructurado de conversión en formato JSON."""
        manifest_data = {
            "source_path": str(result.source_path),
            "output_path": str(result.output_path),
            "elements_detected": {
                "paragraphs": result.stats.paragraphs,
                "headings_by_level": result.stats.headings_by_level,
                "tables": result.stats.tables,
                "table_cells": result.stats.table_cells,
                "images": result.stats.images,
                "footnotes": result.stats.footnotes,
            },
            "warnings": result.warnings,
            "processing_time_ms": round(result.duration_ms, 2),
            "status": "SUCCESS" if result.success else "FAILURE",
        }
        manifest_path.write_text(
            json.dumps(manifest_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def convert(
        self, input_path: Union[Path, str], output_path: Union[Path, str]
    ) -> ConversionResult:
        """Ejecuta la pipeline de conversión de DOCX a Markdown.

        Args:
            input_path: Ruta al archivo DOCX de origen.
            output_path: Ruta de destino para el archivo .md generado.

        Returns:
            ConversionResult con métricas y estado del proceso.
        """
        start_time = time.perf_counter()
        in_p = Path(input_path).resolve()
        out_p = Path(output_path).resolve()

        # Ingesta y análisis semántico
        elements = self.reader.read(in_p, self.config)

        # Creación de carpetas de salida si no existen
        out_p.parent.mkdir(parents=True, exist_ok=True)

        # Extracción y guardado de recursos binarios
        self._save_images(elements, out_p.parent)

        # Renderizado de Markdown y recopilación de métricas
        markdown_text, warnings, stats = self.formatter.format_elements(elements)

        # Escritura del documento Markdown
        out_p.write_text(markdown_text, encoding="utf-8")

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        result = ConversionResult(
            source_path=in_p,
            output_path=out_p,
            stats=stats,
            warnings=warnings,
            duration_ms=duration_ms,
            success=True,
        )

        if self.config.emit_manifest:
            manifest_path = out_p.parent / "conversion_manifest.json"
            self._write_manifest(manifest_path, result)

        return result
