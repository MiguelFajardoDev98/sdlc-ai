#!/usr/bin/env python3
"""
Script de compilación y post-procesamiento bajo Normas APA 7.ª edición
para los entregables de tesis del framework SDLC-AI.

Uso:
    python3 scripts/build_apa_deliverable.py [1|2|3|all] [--with-pdf]
"""

import sys
import subprocess
from pathlib import Path
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE_DIR = Path(__file__).resolve().parent.parent
ENTREGABLES_DIR = BASE_DIR / "Entregables"
BIB_FILE = ENTREGABLES_DIR / "referencias.bib"
CSL_FILE = Path("/home/admin/.local/share/pandoc/csl/apa.csl")
REF_DOCX = Path("/home/admin/Projects/Agent_Skills/academico/templates/custom-reference.docx")
FIX_SCRIPT = Path("/home/admin/Projects/Agent_Skills/academico/scripts/fix_apa_docx.py")

TARGETS = {
    "1": "SDLC-AI_Tesis_Entrega1",
    "2": "SDLC-AI_Tesis_Entrega2",
    "3": "SDLC-AI_Tesis_Entrega3_Final",
}


def compile_with_pandoc(doc_md: Path, docx_out: Path) -> None:
    print(f"[1/3] Compilando {doc_md.name} a DOCX con Pandoc + Citeproc + ToC (APA 7)...")
    cmd = [
        "pandoc",
        str(doc_md),
        f"--resource-path=.:{ENTREGABLES_DIR}:{ENTREGABLES_DIR / 'imagenes'}",
        "--toc",
        "--toc-depth=3",
        "-M",
        "toc-title=Tabla de contenidos",
        "--citeproc",
        f"--csl={CSL_FILE}",
        f"--bibliography={BIB_FILE}",
        f"--reference-doc={REF_DOCX}",
        "-o",
        str(docx_out),
    ]
    subprocess.run(cmd, check=True)
    print(f"  -> Pandoc completado: {docx_out.name}")


def run_table_indent_fix(docx_out: Path) -> None:
    print("[2/3] Ejecutando fix_apa_docx.py para eliminar sangría en tablas...")
    cmd = ["python3", str(FIX_SCRIPT), str(docx_out)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if res.stdout.strip():
        print(f"  -> {res.stdout.strip()}")


def _set_border_element(parent: OxmlElement, edge: str, val: str, sz: str = "8", color: str = "000000") -> None:
    """Configura un borde XML explícito en WordprocessingML."""
    el = parent.find(qn(f"w:{edge}"))
    if el is None:
        el = OxmlElement(f"w:{edge}")
        parent.append(el)
    el.set(qn("w:val"), val)
    if val != "none":
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
    else:
        for attr in ("w:sz", "w:space", "w:color"):
            if qn(attr) in el.attrib:
                del el.attrib[qn(attr)]


def apply_apa7_table_borders(table: docx.table.Table) -> None:
    """Aplica bordes horizontales APA 7ma en color negro sólido (#000000):
    - Borde superior de la tabla (1 pt negro)
    - Borde inferior del encabezado (1 pt negro)
    - Borde inferior de la tabla (1 pt negro)
    - Sin bordes verticales ni rejilla interna
    """
    tbl_pr = table._tbl.tblPr
    tbl_borders = tbl_pr.find(qn("w:tblBorders"))
    if tbl_borders is None:
        tbl_borders = OxmlElement("w:tblBorders")
        tbl_pr.append(tbl_borders)

    _set_border_element(tbl_borders, "top", "single", sz="10", color="000000")
    _set_border_element(tbl_borders, "bottom", "single", sz="10", color="000000")
    _set_border_element(tbl_borders, "left", "none")
    _set_border_element(tbl_borders, "right", "none")
    _set_border_element(tbl_borders, "insideH", "none")
    _set_border_element(tbl_borders, "insideV", "none")

    num_rows = len(table.rows)
    for row_idx, row in enumerate(table.rows):
        is_header = row_idx == 0
        is_last = row_idx == num_rows - 1
        for cell in row.cells:
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_borders = tc_pr.find(qn("w:tcBorders"))
            if tc_borders is None:
                tc_borders = OxmlElement("w:tcBorders")
                tc_pr.append(tc_borders)

            if is_header:
                _set_border_element(tc_borders, "top", "single", sz="10", color="000000")
                _set_border_element(tc_borders, "bottom", "single", sz="8", color="000000")
            elif is_last:
                _set_border_element(tc_borders, "top", "none")
                _set_border_element(tc_borders, "bottom", "single", sz="10", color="000000")
            else:
                _set_border_element(tc_borders, "top", "none")
                _set_border_element(tc_borders, "bottom", "none")

            _set_border_element(tc_borders, "left", "none")
            _set_border_element(tc_borders, "right", "none")

            tc_mar = tc_pr.find(qn("w:tcMar"))
            if tc_mar is None:
                tc_mar = OxmlElement("w:tcMar")
                tc_pr.append(tc_mar)
            for side, dxa in (("top", "80"), ("bottom", "80"), ("left", "108"), ("right", "108")):
                m_el = tc_mar.find(qn(f"w:{side}"))
                if m_el is None:
                    m_el = OxmlElement(f"w:{side}")
                    tc_mar.append(m_el)
                m_el.set(qn("w:w"), dxa)
                m_el.set(qn("w:type"), "dxa")

            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent = Inches(0)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05
                if is_header:
                    for run in p.runs:
                        run.bold = True


def postprocess_apa_typography(docx_out: Path) -> None:
    print("[3/3] Aplicando reglas tipográficas APA 7ma (márgenes, figuras y bordes negros en tablas)...")
    doc = docx.Document(str(docx_out))

    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    for table in doc.tables:
        apply_apa7_table_borders(table)

    for p in doc.paragraphs:
        txt = p.text.strip()

        if p.style.name.startswith("Heading"):
            p.paragraph_format.keep_with_next = True

        if (txt.startswith("Figura ") or txt.startswith("**Figura ")) and len(txt) < 40:
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0

        if p.runs and p.runs[0].italic and 10 < len(txt) < 140 and not txt.startswith("Nota"):
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.0

        if len(p._p.xpath(".//w:drawing")) > 0:
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.0

        if txt.startswith("Nota.") or txt.startswith("*Nota.*"):
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(14)
            p.paragraph_format.line_spacing = 1.15

        if (txt.startswith("Tabla ") or txt.startswith("**Tabla ")) and len(txt) < 40:
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0

    doc.save(str(docx_out))
    print(f"  -> Guardado {docx_out} ({len(doc.tables)} tablas formateadas con bordes APA 7)")


def export_to_pdf(docx_out: Path) -> None:
    print(f"[Opcional] Exportando {docx_out.name} a PDF con LibreOffice...")
    cmd = [
        "libreoffice",
        "-env:UserInstallation=file:///tmp/lo_test",
        "--headless",
        "--convert-to",
        "pdf",
        str(docx_out),
        "--outdir",
        str(ENTREGABLES_DIR),
    ]
    subprocess.run(cmd, check=True)
    print(f"  -> PDF generado: {docx_out.with_suffix('.pdf')}")


def build_target(stem: str, with_pdf: bool = False) -> None:
    doc_md = ENTREGABLES_DIR / f"{stem}.md"
    docx_out = ENTREGABLES_DIR / f"{stem}.docx"
    if not doc_md.is_file():
        raise FileNotFoundError(f"No se encontró el archivo fuente: {doc_md}")
    print(f"\n=== COMPILANDO {stem} (APA 7MA EDICIÓN — SOLO DOCX) ===")
    compile_with_pandoc(doc_md, docx_out)
    run_table_indent_fix(docx_out)
    postprocess_apa_typography(docx_out)
    if with_pdf:
        export_to_pdf(docx_out)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    with_pdf = "--with-pdf" in sys.argv[1:]
    arg = args[0] if args else "2"
    if arg == "all":
        for stem in TARGETS.values():
            build_target(stem, with_pdf=with_pdf)
    elif arg in TARGETS:
        build_target(TARGETS[arg], with_pdf=with_pdf)
    else:
        print("Uso: python3 scripts/build_apa_deliverable.py [1|2|3|all] [--with-pdf]")
        sys.exit(1)
    print("\n=== PROCESO COMPLETADO EXITOSAMENTE ===")


if __name__ == "__main__":
    main()
