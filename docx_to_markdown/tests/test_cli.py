"""Pruebas para la interfaz de línea de comandos (CLI) de docx_to_markdown."""

from pathlib import Path

from docx_to_markdown.cli import build_parser, main


def test_build_parser() -> None:
    """Verifica la definición y opciones del analizador de argumentos."""
    parser = build_parser()
    args = parser.parse_args(["--input", "doc.docx", "--output", "out.md"])
    assert args.input == Path("doc.docx")
    assert args.output == Path("out.md")
    assert args.extract_images is True
    assert args.emit_manifest is True


def test_cli_execution_success(sample_docx_fixture: Path, tmp_path: Path) -> None:
    """Verifica la ejecución exitosa de la CLI devolviendo código 0."""
    out_md = tmp_path / "cli_out.md"
    argv = ["--input", str(sample_docx_fixture), "--output", str(out_md)]
    exit_code = main(argv)

    assert exit_code == 0
    assert out_md.exists()


def test_cli_execution_failure(corrupted_docx_fixture: Path, tmp_path: Path) -> None:
    """Verifica que un archivo corrupto devuelva código 1 sin excepciones no capturadas."""
    out_md = tmp_path / "cli_bad.md"
    argv = ["--input", str(corrupted_docx_fixture), "--output", str(out_md)]
    exit_code = main(argv)

    assert exit_code == 1
    assert not out_md.exists()
