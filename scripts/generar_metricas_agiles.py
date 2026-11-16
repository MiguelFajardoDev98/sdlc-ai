#!/usr/bin/env python3
"""Generador de Métricas de Gestión Ágil y Figuras Académicas (300 DPI).

Produce:
1. logs/metricas_gestion_proyecto.json (datos de Puntos de Historia, Burndown y Velocidad).
2. Entregables/imagenes/figura_06_release_burndown.png
3. Entregables/imagenes/figura_07_sprint_burndown.png
4. Entregables/imagenes/figura_08_informe_velocidad.png
5. Entregables/imagenes/figura_09_reporte_excel_reposicion.png
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "Entregables" / "imagenes"
LOGS_DIR = BASE_DIR / "logs"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
    }
)

USER_STORIES: List[Dict[str, Any]] = [
    {"sprint": "Sprint 1", "id": "HU-01", "titulo": "Validación SKU MODELO-TALLA-COLOR", "modulo": "data_ingestion.py", "ph": 3, "t_trad_h": 9.0, "t_sdlc_h": 2.10},
    {"sprint": "Sprint 1", "id": "HU-02", "titulo": "Ingesta CSV y sanitización", "modulo": "data_ingestion.py", "ph": 2, "t_trad_h": 6.0, "t_sdlc_h": 1.40},
    {"sprint": "Sprint 1", "id": "HU-03", "titulo": "Cálculo de DCI y TQS", "modulo": "kpi_calculator.py", "ph": 3, "t_trad_h": 9.0, "t_sdlc_h": 2.05},
    {"sprint": "Sprint 2", "id": "HU-04", "titulo": "Clasificación de alertas en 4 niveles", "modulo": "alert_engine.py", "ph": 5, "t_trad_h": 15.0, "t_sdlc_h": 2.70},
    {"sprint": "Sprint 2", "id": "HU-05", "titulo": "Detección de traslados entre tiendas", "modulo": "alert_engine.py", "ph": 5, "t_trad_h": 15.0, "t_sdlc_h": 2.75},
    {"sprint": "Sprint 2", "id": "HU-06", "titulo": "Reporte de reposición en Excel", "modulo": "replenishment_exporter.py", "ph": 3, "t_trad_h": 9.0, "t_sdlc_h": 1.63},
    {"sprint": "Sprint 3", "id": "HU-07", "titulo": "Informe ejecutivo con Gemini Pro", "modulo": "gemini_reporter.py", "ph": 5, "t_trad_h": 15.0, "t_sdlc_h": 2.52},
    {"sprint": "Sprint 3", "id": "HU-08", "titulo": "Respaldo determinista sin conexión", "modulo": "gemini_reporter.py", "ph": 3, "t_trad_h": 9.0, "t_sdlc_h": 1.52},
    {"sprint": "Sprint 4", "id": "HU-09", "titulo": "Orquestador CLI de flujo completo", "modulo": "main.py", "ph": 3, "t_trad_h": 9.0, "t_sdlc_h": 2.67},
    {"sprint": "Sprint 4", "id": "HU-10", "titulo": "Script portable y control de calidad", "modulo": "run.sh", "ph": 2, "t_trad_h": 6.0, "t_sdlc_h": 1.78},
    {"sprint": "Sprint 4", "id": "HU-11", "titulo": "Telemetría de tiempos y ahorro", "modulo": "main.py", "ph": 1, "t_trad_h": 3.0, "t_sdlc_h": 0.89},
]

SPRINT_SUMMARY: List[Dict[str, Any]] = [
    {"sprint": "Sprint 1", "nombre": "Ingesta y KPIs", "ph_planeados": 8, "ph_completados": 8, "t_trad_h": 24.0, "t_sdlc_h": 5.55},
    {"sprint": "Sprint 2", "nombre": "Alertas y Excel", "ph_planeados": 13, "ph_completados": 13, "t_trad_h": 39.0, "t_sdlc_h": 7.08},
    {"sprint": "Sprint 3", "nombre": "Gemini Pro", "ph_planeados": 8, "ph_completados": 8, "t_trad_h": 24.0, "t_sdlc_h": 4.04},
    {"sprint": "Sprint 4", "nombre": "DevOps y Cierre", "ph_planeados": 6, "ph_completados": 6, "t_trad_h": 18.0, "t_sdlc_h": 5.34},
]


def export_agile_json() -> Path:
    """Exporta las métricas consolidadas a logs/metricas_gestion_proyecto.json."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    total_ph = sum(s["ph_completados"] for s in SPRINT_SUMMARY)
    total_trad_h = round(sum(s["t_trad_h"] for s in SPRINT_SUMMARY), 2)
    total_sdlc_h = round(sum(s["t_sdlc_h"] for s in SPRINT_SUMMARY), 2)

    sprints_enriched = []
    remaining = total_ph
    release_burndown = [{"hito": "Inicio", "ph_restantes": remaining}]
    for s in SPRINT_SUMMARY:
        remaining -= s["ph_completados"]
        vel_trad = round(s["ph_completados"] / s["t_trad_h"], 2)
        vel_sdlc = round(s["ph_completados"] / s["t_sdlc_h"], 2)
        sprints_enriched.append(
            {
                **s,
                "cumplimiento_pct": 100.0,
                "velocidad_trad_ph_hora": vel_trad,
                "velocidad_sdlc_ph_hora": vel_sdlc,
                "factor_aceleracion": round(vel_sdlc / vel_trad, 2),
                "ph_restantes_cierre": remaining,
            }
        )
        release_burndown.append({"hito": s["sprint"], "ph_restantes": remaining})

    payload = {
        "total_puntos_historia": total_ph,
        "total_historias_usuario": len(USER_STORIES),
        "esfuerzo_tradicional_horas": total_trad_h,
        "tiempo_real_sdlc_ai_horas": total_sdlc_h,
        "reduccion_tiempo_pct": round(((total_trad_h - total_sdlc_h) / total_trad_h) * 100, 2),
        "velocidad_promedio_trad_ph_hora": round(total_ph / total_trad_h, 2),
        "velocidad_promedio_sdlc_ph_hora": round(total_ph / total_sdlc_h, 2),
        "factor_aceleracion_global": round((total_ph / total_sdlc_h) / (total_ph / total_trad_h), 2),
        "sprints": sprints_enriched,
        "release_burndown": release_burndown,
        "historias_usuario": USER_STORIES,
    }
    out_file = LOGS_DIR / "metricas_gestion_proyecto.json"
    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_file


def plot_release_burndown() -> None:
    """Genera figura_06_release_burndown.png."""
    etiquetas = ["Inicio", "Sprint 1\n(Ingesta)", "Sprint 2\n(Alertas/Excel)", "Sprint 3\n(Gemini Pro)", "Sprint 4\n(DevOps/Cierre)"]
    x = np.arange(len(etiquetas))
    ideal = [35, 26.25, 17.5, 8.75, 0]
    real = [35, 27, 14, 6, 0]

    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    ax.plot(x, ideal, linestyle="--", color="#7F8C8D", linewidth=2, marker="o", label="Línea ideal de avance (8,75 PH/sprint)")
    ax.plot(x, real, color="#1B365D", linewidth=2.8, marker="s", markersize=8, label="Trabajo pendiente real (SDLC-AI)")
    ax.fill_between(x, real, alpha=0.10, color="#1B365D")

    for xi, yi in zip(x, real):
        ax.annotate(f"{yi} PH", (xi, yi), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, fontweight="bold", color="#1B365D")

    ax.set_title("Gráfica Burndown General del Proyecto (35 Puntos de Historia)", fontsize=12, fontweight="bold", pad=14, color="#1A1A1A")
    ax.set_ylabel("Puntos de Historia Pendientes (PH)", fontsize=10, fontweight="bold")
    ax.set_xlabel("Iteraciones del Proyecto", fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontsize=9)
    ax.set_ylim(-2, 40)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(IMG_DIR / "figura_06_release_burndown.png", dpi=300)
    plt.close(fig)


def plot_sprint_burndown() -> None:
    """Genera figura_07_sprint_burndown.png."""
    fases = ["Inicio\nSprint", "Especificación\nEARS", "Diseño y\nCódigo", "Pruebas\ny QA", "Cierre\nSprint"]
    x = np.arange(len(fases))

    sprints_curves = [
        ("Sprint 1 (8 PH)", [8, 6, 3, 1, 0], "#1B365D", "o"),
        ("Sprint 2 (13 PH)", [13, 10, 5, 2, 0], "#2E86C1", "s"),
        ("Sprint 3 (8 PH)", [8, 6, 3, 1, 0], "#117A65", "^"),
        ("Sprint 4 (6 PH)", [6, 5, 2, 1, 0], "#B9770E", "D"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(9.5, 6.2), dpi=300, sharex=True)
    for ax, (titulo, real, color, marker) in zip(axes.flat, sprints_curves):
        ideal = np.linspace(real[0], 0, len(fases))
        ax.plot(x, ideal, linestyle="--", color="#95A5A6", linewidth=1.6, label="Ideal")
        ax.plot(x, real, color=color, linewidth=2.4, marker=marker, markersize=6, label="Avance real")
        for xi, yi in zip(x, real):
            ax.annotate(f"{yi}", (xi, yi), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8, fontweight="bold", color=color)
        ax.set_title(titulo, fontsize=10.5, fontweight="bold", color="#1A1A1A")
        ax.set_ylabel("PH Pendientes", fontsize=8.5)
        ax.set_ylim(-1, real[0] + 2.5)
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="upper right", fontsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    for ax in axes[1]:
        ax.set_xticks(x)
        ax.set_xticklabels(fases, fontsize=8)

    fig.suptitle("Gráficas Burndown por Sprint según Hitos de Ejecución", fontsize=12.5, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(IMG_DIR / "figura_07_sprint_burndown.png", dpi=300)
    plt.close(fig)


def plot_velocity_report() -> None:
    """Genera figura_08_informe_velocidad.png."""
    nombres = [f"{s['sprint']}\n({s['nombre']})" for s in SPRINT_SUMMARY]
    planeados = [s["ph_planeados"] for s in SPRINT_SUMMARY]
    completados = [s["ph_completados"] for s in SPRINT_SUMMARY]
    vel_trad = [round(s["ph_completados"] / s["t_trad_h"], 2) for s in SPRINT_SUMMARY]
    vel_sdlc = [round(s["ph_completados"] / s["t_sdlc_h"], 2) for s in SPRINT_SUMMARY]
    x = np.arange(len(nombres))
    width = 0.34

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), dpi=300)

    # Panel 1: PH Planeados vs Completados
    b1 = ax1.bar(x - width / 2, planeados, width, label="PH Planeados", color="#AEB6BF", edgecolor="#566573")
    b2 = ax1.bar(x + width / 2, completados, width, label="PH Completados", color="#1B365D", edgecolor="#152947")
    ax1.axhline(8.75, color="#C0392B", linestyle="--", linewidth=1.4, label="Velocidad media (8,75 PH/sprint)")
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax1.annotate(f"{int(h)}", (bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5, fontweight="bold")
    ax1.set_title("Cumplimiento de Puntos de Historia por Sprint", fontsize=10.5, fontweight="bold")
    ax1.set_ylabel("Puntos de Historia (PH)", fontsize=9.5, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(nombres, fontsize=8)
    ax1.set_ylim(0, 16)
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper right", fontsize=8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Panel 2: Velocidad horaria (PH/hora)
    b3 = ax2.bar(x - width / 2, vel_trad, width, label="Referencia tradicional (PH/h)", color="#BDC3C7", edgecolor="#7F8C8D")
    b4 = ax2.bar(x + width / 2, vel_sdlc, width, label="Framework SDLC-AI (PH/h)", color="#117A65", edgecolor="#0B5345")
    for bar in list(b3) + list(b4):
        h = bar.get_height()
        ax2.annotate(f"{h:.2f}", (bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8, fontweight="bold")
    ax2.set_title("Rendimiento Efectivo (PH por Hora Invertida)", fontsize=10.5, fontweight="bold")
    ax2.set_ylabel("Velocidad (PH / hora)", fontsize=9.5, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(nombres, fontsize=8)
    ax2.set_ylim(0, 2.4)
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.suptitle("Informe de Velocidad del Proyecto SDLC-AI", fontsize=12.5, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(IMG_DIR / "figura_08_informe_velocidad.png", dpi=300)
    plt.close(fig)


def plot_excel_preview() -> None:
    """Genera figura_09_reporte_excel_reposicion.png a partir del Excel real generado."""
    excel_path = LOGS_DIR / "reporte_reposicion_inventario.xlsx"
    if not excel_path.exists():
        return

    df_detail = pd.read_excel(excel_path, sheet_name="Orden_Reposicion_SKU").head(8)
    df_sum = pd.read_excel(excel_path, sheet_name="Resumen_Ejecutivo_Tiendas")

    cols = ["SKU", "Ciudad", "Stock_Actual", "DCI_Dias_Cobertura", "Estado_Alerta", "Unidades_Sugeridas_Reposicion", "Inversion_Estimada_COP"]
    df_view = df_detail[cols].copy()
    df_view.columns = ["SKU", "Ciudad", "Stock", "DCI (días)", "Estado Alerta", "Unid. Sugeridas", "Inversión (COP)"]
    df_view["Inversión (COP)"] = df_view["Inversión (COP)"].apply(lambda v: f"${int(v):,}")

    fig, (ax_tbl, ax_sum) = plt.subplots(2, 1, figsize=(10.5, 6.2), dpi=300, gridspec_kw={"height_ratios": [2.2, 1.3]})
    ax_tbl.axis("off")
    ax_tbl.set_title("Hoja 1: Orden_Reposicion_SKU (Primeras 8 de 203 referencias priorizadas por DCI)", fontsize=10.5, fontweight="bold", loc="left", pad=6)

    table = ax_tbl.table(
        cellText=df_view.values,
        colLabels=df_view.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.45)

    for (row_idx, col_idx), cell in table.get_celld().items():
        if row_idx == 0:
            cell.set_facecolor("#1B365D")
            cell.set_text_props(color="white", weight="bold")
        elif col_idx == 4:
            val = cell.get_text().get_text()
            if "CRÍTICO" in val:
                cell.set_facecolor("#FADBD8")
                cell.set_text_props(color="#922B21", weight="bold")
            else:
                cell.set_facecolor("#FCF3CF")
                cell.set_text_props(color="#7D6608", weight="bold")
        elif row_idx % 2 == 0:
            cell.set_facecolor("#F8F9F9")

    # Panel inferior: Resumen financiero por ciudad
    ax_sum.barh(df_sum["Ciudad"], df_sum["Inversion_Total_COP"] / 1e6, color="#2E86C1", edgecolor="#1B4F72")
    for idx, row in enumerate(df_sum.itertuples()):
        ax_sum.text(
            (row.Inversion_Total_COP / 1e6) + 0.8,
            idx,
            f"${row.Inversion_Total_COP / 1e6:.1f} M ({row.SKUs_en_Riesgo} SKUs)",
            va="center",
            fontsize=8.5,
            fontweight="bold",
        )
    ax_sum.set_title("Hoja 2: Resumen_Ejecutivo_Tiendas — Inversión Sugerida por Ciudad (Millones COP)", fontsize=10.5, fontweight="bold", loc="left")
    ax_sum.set_xlabel("Inversión Estimada de Reposición (Millones COP)", fontsize=9)
    ax_sum.set_xlim(0, max(df_sum["Inversion_Total_COP"] / 1e6) * 1.28)
    ax_sum.grid(axis="x", linestyle=":", alpha=0.5)
    ax_sum.spines["top"].set_visible(False)
    ax_sum.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(IMG_DIR / "figura_09_reporte_excel_reposicion.png", dpi=300)
    plt.close(fig)


def plot_ab_benchmark_comparison() -> None:
    """Genera la Figura 10: Comparación empírica A/B de velocidad, calidad y resiliencia."""
    fig, (ax_time, ax_qual, ax_debt) = plt.subplots(
        1, 3, figsize=(14.0, 4.4), gridspec_kw={"width_ratios": [1.1, 1.4, 1.0]}
    )

    w = 0.35

    # Panel 1: Telemetría Medida de Ejecución (Tiempo y Actividad Agéntica)
    conceptos_tiempo = [
        "Tiempo Medido\nEjecución (min)",
        "Pasos de\nPlanificación",
        "Llamadas a\nHerramientas",
        "Pruebas Unitarias\nGeneradas",
    ]
    tiempo_a = [7.9, 14.0, 13.0, 6.0]
    tiempo_b = [15.0, 27.0, 47.0, 11.0]
    x_t = list(range(len(conceptos_tiempo)))

    b_t_a = ax_time.bar([i - w / 2 for i in x_t], tiempo_a, width=w, label="Sesión A: Sin Arnés", color="#95A5A6", edgecolor="#566573")
    b_t_b = ax_time.bar([i + w / 2 for i in x_t], tiempo_b, width=w, label="Sesión B: SDLC-AI", color="#1F618D", edgecolor="#154360")

    ax_time.set_xticks(x_t)
    ax_time.set_xticklabels(conceptos_tiempo, fontsize=7.8)
    ax_time.set_ylim(0, 56)
    ax_time.set_ylabel("Valor Medido en Sesión", fontsize=9.0)
    ax_time.set_title("A. Telemetría Medida de Ejecución", fontsize=10.0, fontweight="bold")
    ax_time.legend(loc="upper left", fontsize=7.5)
    ax_time.grid(axis="y", linestyle=":", alpha=0.5)
    ax_time.spines["top"].set_visible(False)
    ax_time.spines["right"].set_visible(False)

    for idx_b, b in enumerate(b_t_a):
        h = b.get_height()
        lbl = f"{h:.1f}m" if idx_b == 0 else f"{int(h)}"
        ax_time.text(b.get_x() + b.get_width() / 2, h + 1.0, lbl, ha="center", va="bottom", fontsize=7.5, color="#2C3E50", fontweight="bold")
    for idx_b, b in enumerate(b_t_b):
        h = b.get_height()
        lbl = f"{h:.1f}m" if idx_b == 0 else f"{int(h)}"
        ax_time.text(b.get_x() + b.get_width() / 2, h + 1.0, lbl, ha="center", va="bottom", fontsize=7.5, color="#154360", fontweight="bold")

    # Panel 2: Calidad Técnica y Resiliencia (%)
    categorias_qual = [
        "Calidad Estática\n(Pylint %)",
        "Cobertura Pruebas\n(Pytest-cov %)",
        "Pruebas Ciegas\nFuncionales (%)",
        "Pruebas Ciegas\nFrontera / Caos (%)",
        "Efectividad Global\nBatería Ciega (%)",
    ]
    sesion_a = [89.2, 75.0, 100.0, 40.0, 70.0]
    sesion_b = [100.0, 97.0, 100.0, 100.0, 100.0]
    x_q = list(range(len(categorias_qual)))

    bars_a = ax_qual.bar([i - w / 2 for i in x_q], sesion_a, width=w, label="Sesión A: Sin Arnés", color="#95A5A6", edgecolor="#566573")
    bars_b = ax_qual.bar([i + w / 2 for i in x_q], sesion_b, width=w, label="Sesión B: SDLC-AI", color="#1F618D", edgecolor="#154360")

    ax_qual.axhline(85.0, color="#C0392B", linestyle="--", linewidth=1.0, label="Meta Calidad (85%)")
    ax_qual.set_xticks(x_q)
    ax_qual.set_xticklabels(categorias_qual, fontsize=7.8)
    ax_qual.set_ylim(0, 116)
    ax_qual.set_ylabel("Porcentaje de Cumplimiento (%)", fontsize=9.0)
    ax_qual.set_title("B. Indicadores de Calidad y Resiliencia", fontsize=10.0, fontweight="bold")
    ax_qual.legend(loc="lower right", fontsize=7.5, framealpha=0.95)
    ax_qual.grid(axis="y", linestyle=":", alpha=0.5)
    ax_qual.spines["top"].set_visible(False)
    ax_qual.spines["right"].set_visible(False)

    for b in bars_a:
        h = b.get_height()
        ax_qual.text(b.get_x() + b.get_width() / 2, h + 1.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=7.4, color="#2C3E50")
    for b in bars_b:
        h = b.get_height()
        ax_qual.text(b.get_x() + b.get_width() / 2, h + 1.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=7.4, fontweight="bold", color="#154360")

    # Panel 3: Deuda técnica y defectos residuales
    metricas_deuda = ["Advertencias\nPylint", "Defectos en\nPruebas Caos", "Artefactos EARS\ny Diseño"]
    val_a = [69, 3, 0]
    val_b = [0, 0, 5]
    x_d = list(range(len(metricas_deuda)))

    b2_a = ax_debt.bar([i - w / 2 for i in x_d], val_a, width=w, label="Sesión A: Sin Arnés", color="#E67E22", edgecolor="#A04000")
    b2_b = ax_debt.bar([i + w / 2 for i in x_d], val_b, width=w, label="Sesión B: SDLC-AI", color="#27AE60", edgecolor="#196F3D")

    ax_debt.set_xticks(x_d)
    ax_debt.set_xticklabels(metricas_deuda, fontsize=8.0)
    ax_debt.set_ylim(0, 80)
    ax_debt.set_ylabel("Conteo de Elementos", fontsize=9.0)
    ax_debt.set_title("C. Deuda Técnica vs. Artefactos", fontsize=10.0, fontweight="bold")
    ax_debt.legend(loc="upper right", fontsize=7.5)
    ax_debt.grid(axis="y", linestyle=":", alpha=0.5)
    ax_debt.spines["top"].set_visible(False)
    ax_debt.spines["right"].set_visible(False)

    for b in b2_a:
        h = b.get_height()
        ax_debt.text(b.get_x() + b.get_width() / 2, h + 1.5, f"{int(h)}", ha="center", va="bottom", fontsize=8.0, fontweight="bold", color="#A04000")
    for b in b2_b:
        h = b.get_height()
        ax_debt.text(b.get_x() + b.get_width() / 2, h + 1.5, f"{int(h)}", ha="center", va="bottom", fontsize=8.0, fontweight="bold", color="#196F3D")

    plt.tight_layout()
    plt.savefig(IMG_DIR / "figura_10_benchmark_comparativo_ab.png", dpi=300)
    plt.close(fig)


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    json_path = export_agile_json()
    plot_release_burndown()
    plot_sprint_burndown()
    plot_velocity_report()
    plot_excel_preview()
    plot_ab_benchmark_comparison()
    print(f"Métricas ágiles exportadas en: {json_path}")
    print(f"Figuras generadas en: {IMG_DIR}")


if __name__ == "__main__":
    main()
