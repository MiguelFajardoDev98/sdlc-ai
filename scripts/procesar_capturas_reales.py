#!/usr/bin/env python3
"""
Script de procesamiento y vinculación de las capturas de pantalla reales
tomadas por el usuario en GNOME/Fedora.
Copia, asigna DPI=300 y guarda en Entregables/imagenes/ y docs/imagenes/
con los nombres canónicos de la tesis.
"""

import shutil
from pathlib import Path
from PIL import Image

SRC_DIR = Path("/home/admin/Imágenes/Capturas de pantalla")
ENTREGABLES_IMG = Path("/home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/Entregables/imagenes")
DOCS_IMG = Path("/home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/docs/imagenes")

ENTREGABLES_IMG.mkdir(parents=True, exist_ok=True)
DOCS_IMG.mkdir(parents=True, exist_ok=True)

# Mapeo exacto de las capturas reales según el orden del asistente
MAPPING = {
    "Captura desde 2026-10-22 22-31-04.png": [
        "figura_01_estructura_arnes.png",
        "figura_a2_arbol_directorios.png"
    ],
    "Captura desde 2026-10-22 22-32-28.png": [
        "figura_03_pytest_docx_to_markdown.png"
    ],
    "Captura desde 2026-10-22 22-33-17.png": [
        "figura_04_pylint_docx_to_markdown.png"
    ],
    "Captura desde 2026-10-22 22-33-52.png": [
        "figura_05_ejecucion_pipeline_retail.png"
    ],
    "Captura desde 2026-10-22 22-38-16.png": [
        "figura_a1_github_repository.png"
    ],
    "Captura desde 2026-10-22 22-36-13.png": [
        "figura_b1_manifiesto_conversion.png"
    ],
    "Captura desde 2026-10-22 22-36-28.png": [
        "figura_b2_qa_report_json.png"
    ],
    "Captura desde 2026-10-22 22-37-02.png": [
        "figura_c1_dataset_retail_muestra.png"
    ],
    "Captura desde 2026-10-22 22-37-22.png": [
        "figura_c2_reporte_ejecutivo_markdown.png"
    ],
    "Captura desde 2026-10-22 22-37-38.png": [
        "figura_c3_metricas_telemetria.png"
    ],
}


def process_images():
    print("=== PROCESANDO CAPTURAS REALES DE PANTALLA ===")
    for src_name, targets in MAPPING.items():
        src_path = SRC_DIR / src_name
        if not src_path.exists():
            print(f"  [ERROR] No se encontró: {src_name}")
            continue
        
        im = Image.open(src_path)
        print(f"Cargando captura real: {src_name} (Tamaño: {im.size}, Modo: {im.mode})")
        
        for target_name in targets:
            dest1 = ENTREGABLES_IMG / target_name
            dest2 = DOCS_IMG / target_name
            im.save(dest1, dpi=(300, 300))
            im.save(dest2, dpi=(300, 300))
            print(f"  -> Guardada: {target_name}")


if __name__ == "__main__":
    process_images()
