"""Jerarquía de excepciones especializadas para el convertidor DOCX a Markdown."""


class DocxConversionError(Exception):
    """Excepción base para todos los errores del proceso de conversión."""


class DocumentNotFoundError(DocxConversionError, FileNotFoundError):
    """Lanzada cuando el archivo DOCX de origen no existe o es inaccesible."""


class InvalidDocxError(DocxConversionError, ValueError):
    """Lanzada cuando el archivo no es un contenedor OOXML/ZIP válido o está corrupto."""
