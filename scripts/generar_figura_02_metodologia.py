#!/usr/bin/env python3
"""Generador de alta precisión para la Figura 2: Flujo Metodológico en Dos Etapas.

Utiliza matplotlib para garantizar un diseño vectorial sin solapamiento de líneas,
textos o cajas, con tipografía clara y acabado académico profesional a 300 DPI.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = Path(__file__).resolve().parent.parent
ENTREGABLES_IMG = BASE_DIR / "Entregables" / "imagenes"
DOCS_IMG = BASE_DIR / "docs" / "imagenes"


def draw_methodological_flowchart(output_path: Path) -> None:
    # Dimensiones de la figura en pulgadas (relación 16:9 de alta resolución)
    fig, ax = plt.subplots(figsize=(15.2, 9.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Fondo general
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # =========================================================================
    # CONTENEDOR 1: ETAPA 1 (FASE DE ESPECIFICACIÓN ASISTIDA)
    # =========================================================================
    box_e1 = patches.FancyBboxPatch(
        (3, 48), 94, 48,
        boxstyle="round,pad=1.2,rounding_size=1.5",
        facecolor="#F4F8FC", edgecolor="#2B6CB0",
        linewidth=2.2, linestyle="--"
    )
    ax.add_patch(box_e1)

    # Título Etapa 1
    ax.text(
        50, 93.5,
        "ETAPA 1: FASE DE ESPECIFICACIÓN ASISTIDA (COLABORACIÓN INVESTIGADOR - AGENTES)",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#1A365D"
    )
    ax.text(
        50, 91.0,
        "Objetivo: Transformar la necesidad en requisitos formales EARS sin ambigüedades antes de escribir código",
        ha="center", va="center", fontsize=9.5, fontstyle="italic", color="#4A5568"
    )

    # Nodos Etapa 1
    # 1. Investigador Humano
    p_inv = patches.FancyBboxPatch(
        (5.5, 68), 16, 17,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#EBF8FF", edgecolor="#3182CE", linewidth=1.8
    )
    ax.add_patch(p_inv)
    ax.text(13.5, 80.5, "INVESTIGADOR", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#2B6CB0")
    ax.text(13.5, 78.0, "HUMANO", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#2B6CB0")
    ax.text(13.5, 73.0, "• Elicitación de negocio\n• Reglas del problema\n• Validación de supuestos\n• Criterios de aceptación", ha="center", va="center", fontsize=8.0, color="#2D3748")

    # Flecha Inv <-> Analista
    ax.annotate(
        "", xy=(24.5, 76.5), xytext=(21.5, 76.5),
        arrowprops=dict(arrowstyle="<->", color="#2B6CB0", lw=2.0)
    )
    ax.text(23.0, 78.5, "Requerimientos\ny alcance", ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#2B6CB0")

    # 2. Agente Analista
    p_ana = patches.FancyBboxPatch(
        (24.5, 68), 16, 17,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#EBF8FF", edgecolor="#3182CE", linewidth=1.8
    )
    ax.add_patch(p_ana)
    ax.text(32.5, 80.5, "AGENTE ANALISTA", ha="center", va="center", fontsize=10.0, fontweight="bold", color="#2B6CB0")
    ax.text(32.5, 78.0, "(Analyst_Agent)", ha="center", va="center", fontsize=9.0, fontstyle="italic", color="#4A5568")
    ax.text(32.5, 73.0, "• Desglose en historias\n• Sintaxis formal EARS\n• Criterios Gherkin\n• Carga de skills", ha="center", va="center", fontsize=8.0, color="#2D3748")

    # Flecha Analista -> Borrador
    ax.annotate(
        "", xy=(43.5, 76.5), xytext=(40.5, 76.5),
        arrowprops=dict(arrowstyle="->", color="#2B6CB0", lw=2.0)
    )
    ax.text(42.0, 78.5, "Emite borrador\nEARS", ha="center", va="bottom", fontsize=7.8, color="#2B6CB0")

    # 3. Borrador de Requisitos
    p_draft = patches.FancyBboxPatch(
        (43.5, 68), 16, 17,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#EDF2F7", edgecolor="#718096", linewidth=1.8
    )
    ax.add_patch(p_draft)
    ax.text(51.5, 80.5, "BORRADOR SRS", ha="center", va="center", fontsize=10.0, fontweight="bold", color="#2D3748")
    ax.text(51.5, 78.0, "(spec_draft.md)", ha="center", va="center", fontsize=8.8, fontfamily="monospace", color="#4A5568")
    ax.text(51.5, 73.0, "• Historias de Usuario\n• Cláusulas EARS\n• Reglas de frontera\n• Sin aprobar aún", ha="center", va="center", fontsize=8.0, color="#4A5568")

    # Flecha Borrador <-> Auditor
    ax.annotate(
        "", xy=(62.5, 76.5), xytext=(59.5, 76.5),
        arrowprops=dict(arrowstyle="<->", color="#C53030", lw=2.0)
    )
    ax.text(61.0, 78.5, "Auditoría\nestricta", ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#C53030")

    # 4. Agente Auditor
    p_aud = patches.FancyBboxPatch(
        (62.5, 68), 16, 17,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#FFF5F5", edgecolor="#E53E3E", linewidth=1.8
    )
    ax.add_patch(p_aud)
    ax.text(70.5, 80.5, "AGENTE AUDITOR", ha="center", va="center", fontsize=10.0, fontweight="bold", color="#9B2C2C")
    ax.text(70.5, 78.0, "(Auditor_Agent)", ha="center", va="center", fontsize=9.0, fontstyle="italic", color="#742A2A")
    ax.text(70.5, 73.0, "• Detecta ambigüedades\n• Exige verificabilidad\n• audit_report.md\n• Dictamen final", ha="center", va="center", fontsize=8.0, color="#4A5568")

    # Flecha Auditor -> Pausa
    ax.annotate(
        "", xy=(81.5, 76.5), xytext=(78.5, 76.5),
        arrowprops=dict(arrowstyle="->", color="#DD6B20", lw=2.0)
    )
    ax.text(80.0, 78.5, "Dictamen\naprobado", ha="center", va="bottom", fontsize=7.8, color="#DD6B20")

    # 5. Pausa de Seguridad (WAITING_APPROVAL)
    p_wait = patches.FancyBboxPatch(
        (81.5, 68), 14, 17,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#FEFCBF", edgecolor="#D69E2E", linewidth=2.0
    )
    ax.add_patch(p_wait)
    ax.text(88.5, 80.5, "PUNTO DE CONTROL", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#B7791F")
    ax.text(88.5, 78.0, "WAITING_APPROVAL", ha="center", va="center", fontsize=8.5, fontfamily="monospace", color="#975A16")
    ax.text(88.5, 72.8, "Pausa de seguridad:\nRequiere aprobación\nhumana explícita", ha="center", va="center", fontsize=8.0, color="#744210")

    # Fila inferior de Etapa 1: Aprobación humana hacia el Requisito Congelado
    # Flecha vertical desde Pausa hacia abajo
    ax.annotate(
        "", xy=(88.5, 59.5), xytext=(88.5, 68.0),
        arrowprops=dict(arrowstyle="->", color="#D69E2E", lw=2.0)
    )
    ax.text(89.5, 63.8, "Validación\nhumana", ha="left", va="center", fontsize=7.5, color="#B7791F", fontweight="bold")

    # Caja de Acción: Comando de aprobación
    p_cmd = patches.FancyBboxPatch(
        (54.0, 52.0), 38.0, 7.5,
        boxstyle="round,pad=0.6,rounding_size=0.8",
        facecolor="#FEFCBF", edgecolor="#D69E2E", linewidth=1.5
    )
    ax.add_patch(p_cmd)
    ax.text(73.0, 56.5, "COMANDO DE AUTORIZACIÓN:  /approve-spec sprint_XX", ha="center", va="center", fontsize=8.8, fontfamily="monospace", fontweight="bold", color="#975A16")
    ax.text(73.0, 53.8, "El investigador humano valida formalmente que el SRS cumple los objetivos", ha="center", va="center", fontsize=7.8, color="#744210")

    # Flecha desde Comando hacia Requisito Congelado
    ax.annotate(
        "", xy=(48.0, 55.7), xytext=(54.0, 55.7),
        arrowprops=dict(arrowstyle="->", color="#2B6CB0", lw=2.2)
    )

    # Requisito Congelado (Centro inferior de Etapa 1)
    p_srs = patches.FancyBboxPatch(
        (8.0, 51.5), 40.0, 8.5,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#EBF8FF", edgecolor="#2B6CB0", linewidth=2.2
    )
    ax.add_patch(p_srs)
    ax.text(28.0, 57.0, "REQUISITO CONGELADO E INMUTABLE (spec.md v1.0)", ha="center", va="center", fontsize=10.0, fontweight="bold", color="#1A365D")
    ax.text(28.0, 53.8, "Línea base formal de ingeniería • Handoff contractual para el pipeline autónomo", ha="center", va="center", fontsize=8.0, color="#2B6CB0")

    # =========================================================================
    # FLECHA DE TRANSICIÓN INTER-ETAPAS (DESPACHO AL PIPELINE AUTÓNOMO)
    # =========================================================================
    ax.annotate(
        "", xy=(28.0, 44.0), xytext=(28.0, 51.5),
        arrowprops=dict(arrowstyle="->", color="#22543D", lw=3.0)
    )
    ax.text(
        29.5, 47.5,
        "Transición de Estado: Despacho del Sprint al Pipeline Autónomo",
        ha="left", va="center", fontsize=8.8, fontweight="bold", color="#22543D"
    )

    # =========================================================================
    # CONTENEDOR 2: ETAPA 2 (PIPELINE DE EJECUCIÓN AUTÓNOMA)
    # =========================================================================
    box_e2 = patches.FancyBboxPatch(
        (3, 3), 94, 41,
        boxstyle="round,pad=1.2,rounding_size=1.5",
        facecolor="#F0FFF4", edgecolor="#2F855A",
        linewidth=2.2
    )
    ax.add_patch(box_e2)

    # Título Etapa 2
    ax.text(
        50, 41.5,
        "ETAPA 2: PIPELINE DE EJECUCIÓN AUTÓNOMA (SIN INTERVENCIÓN HUMANA)",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#22543D"
    )
    ax.text(
        50, 39.0,
        "Ejecución en ciclo cerrado guiada por contratos técnicos, TDD y compuertas automáticas de calidad",
        ha="center", va="center", fontsize=9.5, fontstyle="italic", color="#2F855A"
    )

    # Nodos Etapa 2
    # 1. Agente Arquitecto
    p_arq = patches.FancyBboxPatch(
        (5.5, 12), 18, 22,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#E6FFFA", edgecolor="#319795", linewidth=1.8
    )
    ax.add_patch(p_arq)
    ax.text(14.5, 30.5, "AGENTE ARQUITECTO", ha="center", va="center", fontsize=10.0, fontweight="bold", color="#234E52")
    ax.text(14.5, 28.0, "(Architect_Agent)", ha="center", va="center", fontsize=9.0, fontstyle="italic", color="#285E61")
    ax.text(14.5, 20.0, "• Diseño modular TDD\n• Contratos de datos\n• Diagramas Mermaid\n• Firmas tipadas\n\nArtefacto de salida:\nspecs/sprint_XX/plan.md", ha="center", va="center", fontsize=8.0, color="#234E52")

    # Flecha Arquitecto -> Desarrollador
    ax.annotate(
        "", xy=(26.5, 23.0), xytext=(23.5, 23.0),
        arrowprops=dict(arrowstyle="->", color="#2F855A", lw=2.2)
    )
    ax.text(25.0, 25.5, "Diseño Técnico\n(plan.md)", ha="center", va="bottom", fontsize=7.8, color="#22543D")

    # 2. Agente Desarrollador
    p_dev = patches.FancyBboxPatch(
        (26.5, 12), 19, 22,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#E6FFFA", edgecolor="#319795", linewidth=1.8
    )
    ax.add_patch(p_dev)
    ax.text(36.0, 30.5, "AGENTE DESARROLLADOR", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#234E52")
    ax.text(36.0, 28.0, "(Developer_Agent)", ha="center", va="center", fontsize=9.0, fontstyle="italic", color="#285E61")
    ax.text(36.0, 20.0, "• Codificación en Python\n• Tipado estricto PEP 484\n• Convenciones PEP 8\n• Desacoplamiento modular\n\nArtefacto de salida:\nsrc/*.py", ha="center", va="center", fontsize=8.0, color="#234E52")

    # Bucle cerrado Desarrollador <-> Tester (Doble flecha espaciada)
    ax.annotate(
        "", xy=(48.5, 26.0), xytext=(45.5, 26.0),
        arrowprops=dict(arrowstyle="->", color="#2F855A", lw=2.0)
    )
    ax.text(47.0, 27.5, "Código para\nverificación", ha="center", va="bottom", fontsize=7.2, color="#22543D")

    ax.annotate(
        "", xy=(45.5, 18.0), xytext=(48.5, 18.0),
        arrowprops=dict(arrowstyle="->", color="#C53030", lw=2.0)
    )
    ax.text(47.0, 13.5, "Reporte fallos\n(iteración ≤ 5)", ha="center", va="top", fontsize=7.2, color="#C53030", fontweight="bold")

    # 3. Agente Tester (Bucle cerrado de QA)
    p_tst = patches.FancyBboxPatch(
        (48.5, 12), 23, 22,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#E6FFFA", edgecolor="#319795", linewidth=2.0
    )
    ax.add_patch(p_tst)
    ax.text(60.0, 30.5, "AGENTE TESTER (QA)", ha="center", va="center", fontsize=10.0, fontweight="bold", color="#234E52")
    ax.text(60.0, 28.0, "(Tester_Agent — Closed-Loop QA)", ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#285E61")
    ax.text(60.0, 20.0, "• Suites automatizadas: tests/test_*.py\n• Cobertura estructural: pytest-cov ≥ 80%\n• Calidad estática: pylint ≥ 7.0 (meta 10/10)\n• Precisión analítica: Macro F1 ≥ 0.80\n\nArtefacto de salida: logs/qa_report.json", ha="center", va="center", fontsize=7.8, color="#234E52")

    # Flecha Tester -> DevOps
    ax.annotate(
        "", xy=(74.5, 23.0), xytext=(71.5, 23.0),
        arrowprops=dict(arrowstyle="->", color="#2F855A", lw=2.2)
    )
    ax.text(73.0, 25.5, "Quality Gates\nSuperados", ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#22543D")

    # 4. Agente DevOps y Métricas
    p_ops = patches.FancyBboxPatch(
        (74.5, 12), 21, 22,
        boxstyle="round,pad=0.8,rounding_size=1.0",
        facecolor="#E6FFFA", edgecolor="#319795", linewidth=1.8
    )
    ax.add_patch(p_ops)
    ax.text(85.0, 30.5, "AGENTE DEVOPS", ha="center", va="center", fontsize=10.0, fontweight="bold", color="#234E52")
    ax.text(85.0, 28.0, "(DevOps_Agent)", ha="center", va="center", fontsize=9.0, fontstyle="italic", color="#285E61")
    ax.text(85.0, 20.0, "• Pipeline de ejecución: run.sh\n• Empaquetado y portabilidad\n• Exportación de reportes\n• Consolidación de telemetría:\n  logs/execution_metrics.json", ha="center", va="center", fontsize=7.8, color="#234E52")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"[OK] Diagrama metodológico generado exitosamente en: {output_path}")


def main():
    dest1 = ENTREGABLES_IMG / "figura_02_diagrama_metodologico.png"
    dest2 = DOCS_IMG / "figura_02_diagrama_metodologico.png"
    draw_methodological_flowchart(dest1)
    if DOCS_IMG.exists():
        import shutil
        shutil.copy2(dest1, dest2)
        print(f"[OK] Copiado a: {dest2}")


if __name__ == "__main__":
    main()
