#!/usr/bin/env python3
"""
Script de compilación y post-procesamiento bajo Normas APA 7.ª edición
para los entregables de tesis del framework SDLC-AI.
Aplica:
- Pandoc con Citeproc y CSL oficial APA 7
- Plantilla custom-reference.docx (sangría francesa en bibliografía, títulos N1-N5)
- Remoción de sangría residual en celdas de tablas (fix_apa_docx.py)
- Centrado y no-sangría en figuras e imágenes
- Vinculación keep_with_next en títulos de figuras, tablas y encabezados
- Conversión limpia a PDF con LibreOffice
"""

import sys
import subprocess
from pathlib import Path
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

BASE_DIR = Path(__file__).resolve().parent.parent
DOC_MD = BASE_DIR / "docs" / "SDLC-AI_Tesis_Entrega1.md"
DOCX_OUT = BASE_DIR / "Entregables" / "SDLC-AI_Tesis_Entrega1.docx"
DOCX_MIRROR = BASE_DIR / "docs" / "SDLC-AI_Tesis_Entrega1.docx"
PDF_OUT = BASE_DIR / "Entregables" / "SDLC-AI_Tesis_Entrega1.pdf"
BIB_FILE = BASE_DIR / "Entregables" / "referencias.bib"
CSL_FILE = Path("/home/admin/.local/share/pandoc/csl/apa.csl")
REF_DOCX = Path("/home/admin/Projects/Agent_Skills/academico/templates/custom-reference.docx")
FIX_SCRIPT = Path("/home/admin/Projects/Agent_Skills/academico/scripts/fix_apa_docx.py")


def compile_with_pandoc():
    print("[1/4] Compilando Markdown a DOCX con Pandoc + Citeproc (APA 7 CSL)...")
    cmd = [
        "pandoc",
        str(DOC_MD),
        "--resource-path=.:docs:Entregables",
        "--citeproc",
        f"--csl={CSL_FILE}",
        f"--bibliography={BIB_FILE}",
        f"--reference-doc={REF_DOCX}",
        "-o",
        str(DOCX_OUT)
    ]
    subprocess.run(cmd, check=True)
    print("  -> Pandoc completado exitosamente.")


def run_table_indent_fix():
    print("[2/4] Ejecutando fix_apa_docx.py para corregir sangrías en tablas...")
    cmd = ["python3", str(FIX_SCRIPT), str(DOCX_OUT)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print(f"  -> {res.stdout.strip()}")


def postprocess_apa_typography():
    print("[3/4] Aplicando reglas tipográficas APA 7ma (márgenes 1 pulgada, centrado de figuras y notas)...")
    doc = docx.Document(str(DOCX_OUT))
    
    # Márgenes estrictos APA 7: 1 pulgada (2.54 cm) en todos los lados
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        
    for p in doc.paragraphs:
        txt = p.text.strip()
        
        # Evitar orfandad en encabezados
        if p.style.name.startswith("Heading"):
            p.paragraph_format.keep_with_next = True
            
        # Etiquetas de figuras (ej. "Figura 1", "Figura A1")
        if (txt.startswith("Figura ") or txt.startswith("**Figura ")) and len(txt) < 35:
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            
        # Títulos de figuras en cursiva que van solos
        if p.runs and p.runs[0].italic and len(txt) > 10 and len(txt) < 120 and not txt.startswith("Nota"):
            # Si el párrafo anterior era etiqueta de figura
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.0
            
        # Párrafos con imágenes incrustadas (w:drawing)
        if len(p._p.xpath(".//w:drawing")) > 0:
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.0
            
        # Notas explicativas al pie de figuras y tablas
        if txt.startswith("Nota.") or txt.startswith("*Nota.*"):
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(14)
            p.paragraph_format.line_spacing = 1.15
            
        # Etiquetas y títulos de tablas
        if (txt.startswith("Tabla ") or txt.startswith("**Tabla ")) and len(txt) < 35:
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0

    # Guardar documento final corregido
    doc.save(str(DOCX_OUT))
    doc.save(str(DOCX_MIRROR))
    print(f"  -> Guardado {DOCX_OUT} y {DOCX_MIRROR}")


def export_to_pdf():
    print("[4/4] Exportando entregable oficial a PDF con LibreOffice...")
    cmd = [
        "libreoffice",
        "-env:UserInstallation=file:///tmp/lo_test",
        "--headless",
        "--convert-to", "pdf",
        str(DOCX_OUT),
        "--outdir", str(BASE_DIR / "Entregables")
    ]
    subprocess.run(cmd, check=True)
    print(f"  -> PDF generado: {PDF_OUT}")


def main():
    print("=== INICIANDO PIPELINE DE COMPILACIÓN ACADÉMICA APA 7MA EDICIÓN ===")
    compile_with_pandoc()
    run_table_indent_fix()
    postprocess_apa_typography()
    export_to_pdf()
    print("=== PROCESO COMPLETADO EXITOSAMENTE ===")


if __name__ == "__main__":
    main()
