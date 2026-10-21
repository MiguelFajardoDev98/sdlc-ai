"""Paquete docx_to_markdown: Conversión de documentos DOCX a Markdown."""

from docx_to_markdown.converter import DocxConverter
from docx_to_markdown.exceptions import (
    DocxConversionError,
    DocumentNotFoundError,
    InvalidDocxError,
)
from docx_to_markdown.models import (
    ConversionConfig,
    ConversionResult,
    ElementStats,
    ElementType,
)

__all__ = [
    "DocxConverter",
    "ConversionConfig",
    "ConversionResult",
    "ElementStats",
    "ElementType",
    "DocxConversionError",
    "DocumentNotFoundError",
    "InvalidDocxError",
]
