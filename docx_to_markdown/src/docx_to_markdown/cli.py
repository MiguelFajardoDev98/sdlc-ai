"""Interfaz de línea de comandos (CLI) para docx_to_markdown."""

import argparse
import sys
from pathlib import Path

from docx_to_markdown.converter import DocxConverter
from docx_to_markdown.exceptions import DocxConversionError
from docx_to_markdown.models import ConversionConfig


def build_parser() -> argparse.ArgumentParser:
    """Construye el analizador de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        prog="python -m docx_to_markdown.cli",
        description="Convierte documentos Microsoft Word (.docx) a Markdown (GFM).",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=Path,
        help="Ruta al archivo DOCX de origen.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Ruta al archivo Markdown de destino (.md).",
    )
    parser.add_argument(
        "--extract-images",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Extrae imágenes en assets/ (por defecto habilitada).",
    )
    parser.add_argument(
        "--emit-manifest",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Genera o suprime el archivo conversion_manifest.json (por defecto habilitado).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de la CLI.

    Args:
        argv: Lista opcional de argumentos (usa sys.argv si es None).

    Returns:
        Código de salida del proceso (0: éxito, 1: error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    config = ConversionConfig(
        extract_images=args.extract_images,
        emit_manifest=args.emit_manifest,
    )

    try:
        converter = DocxConverter(config=config)
        result = converter.convert(input_path=args.input, output_path=args.output)
        print(f"✔ Conversión completada exitosamente en {result.duration_ms:.2f} ms")
        print(f"  Salida: {result.output_path}")
        print(
            f"  Párrafos: {result.stats.paragraphs} | "
            f"Tablas: {result.stats.tables} | "
            f"Imágenes: {result.stats.images}"
        )
        if result.warnings:
            print(f"  Advertencias: {len(result.warnings)}")
            for w in result.warnings:
                print(f"    - {w}")
        return 0
    except DocxConversionError as exc:
        print(f"✖ Error de conversión: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
