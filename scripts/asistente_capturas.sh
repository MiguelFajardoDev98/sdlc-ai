#!/usr/bin/env bash
# ==============================================================================
# ASISTENTE INTERACTIVO DE CAPTURA DE EVIDENCIAS REALES (SDLC-AI - ENTREGA 1)
# ==============================================================================
# Este script ejecuta de forma limpia y ordenada cada comando del proyecto en tu
# terminal real para que puedas tomar las capturas de pantalla auténticas con la
# herramienta de captura de GNOME (tecla 'Impr Pant' / Print Screen).
# ==============================================================================

set -e

DIR_PROYECTO="/home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI"
cd "$DIR_PROYECTO"

# Colores de terminal
C_AZUL="\033[1;34m"
C_VERDE="\033[1;32m"
C_CYAN="\033[1;36m"
C_AMARILLO="\033[1;33m"
C_BLANCO="\033[1;37m"
C_GRIS="\033[0;90m"
C_RESET="\033[0m"

pausar_captura() {
    local figura="$1"
    local nombre_archivo="$2"
    echo ""
    echo -e "${C_AMARILLO}════════════════════════════════════════════════════════════════════════════════${C_RESET}"
    echo -e "${C_VERDE}  📸 PANTALLA LISTA PARA CAPTURAR: ${C_BLANCO}${figura}${C_RESET}"
    echo -e "  Guárdala en: ${C_CYAN}Entregables/imagenes/${nombre_archivo}${C_RESET}"
    echo -e "${C_GRIS}  Tip Fedora/GNOME: Presiona la tecla [Impr Pant] (Print Screen) -> Selecciona 'Ventana'${C_RESET}"
    echo -e "${C_AMARILLO}════════════════════════════════════════════════════════════════════════════════${C_RESET}"
    echo ""
    read -p "Presiona [ENTER] cuando hayas tomado la captura para continuar..." _
}

cmd_figura_1_a2() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ tree -L 2 -I '__pycache__|.git|.pytest_cache'"
    echo ""
    tree -L 2 -I '__pycache__|.git|.pytest_cache'
    pausar_captura "Figura A2 (y Figura 1): Árbol de archivos y contratos" "figura_a2_arbol_directorios.png"
}

cmd_figura_3() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ PYTHONPATH=docx_to_markdown/src pytest --cov=docx_to_markdown/src --cov-report=term-missing docx_to_markdown/tests/"
    echo ""
    PYTHONPATH=docx_to_markdown/src pytest --cov=docx_to_markdown/src --cov-report=term-missing docx_to_markdown/tests/
    pausar_captura "Figura 3: Pruebas unitarias (18/18) y Cobertura (97%) docx_to_markdown" "figura_03_pytest_docx_to_markdown.png"
}

cmd_figura_4() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ PYTHONPATH=docx_to_markdown/src pylint docx_to_markdown/src/"
    echo ""
    PYTHONPATH=docx_to_markdown/src pylint docx_to_markdown/src/
    pausar_captura "Figura 4: Calificación Pylint 10.00/10.00 docx_to_markdown" "figura_04_pylint_docx_to_markdown.png"
}

cmd_figura_5() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ ./run.sh"
    echo ""
    ./run.sh
    pausar_captura "Figura 5: Consola del Pipeline E2E Retail (run.sh, 450 SKUs, Delta T 79.04%)" "figura_05_ejecucion_pipeline_retail.png"
}

cmd_figura_a1() {
    clear
    echo -e "${C_AZUL}Abriendo repositorio oficial en Firefox...${C_RESET}"
    echo "URL: https://github.com/MiguelFajardoDev98/sdlc-ai"
    firefox "https://github.com/MiguelFajardoDev98/sdlc-ai" >/dev/null 2>&1 &
    echo ""
    echo -e "${C_VERDE}Firefox abierto con la página de GitHub.${C_RESET}"
    pausar_captura "Figura A1: Repositorio en GitHub" "figura_a1_github_repository.png"
}

cmd_figura_b1() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ cat docx_to_markdown/docs/conversion_manifest.json | python3 -m json.tool"
    echo ""
    cat docx_to_markdown/docs/conversion_manifest.json | python3 -m json.tool
    pausar_captura "Figura B1: Manifiesto JSON de Conversión" "figura_b1_manifiesto_conversion.png"
}

cmd_figura_b2() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ cat logs/qa_report_sprint_01_conversion.json | python3 -m json.tool"
    echo ""
    cat logs/qa_report_sprint_01_conversion.json | python3 -m json.tool
    pausar_captura "Figura B2: Certificación de Quality Gates JSON" "figura_b2_qa_report_json.png"
}

cmd_figura_c1() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ head -n 12 data/synthetic_retail_data.csv | column -t -s,"
    echo ""
    head -n 12 data/synthetic_retail_data.csv | column -t -s,
    pausar_captura "Figura C1: Dataset sintético de Retail (MODELO-TALLA-COLOR)" "figura_c1_dataset_retail_muestra.png"
}

cmd_figura_c2() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ cat logs/executive_report.md"
    echo ""
    cat logs/executive_report.md
    pausar_captura "Figura C2: Informe ejecutivo narrativo de inventarios" "figura_c2_reporte_ejecutivo_markdown.png"
}

cmd_figura_c3() {
    clear
    echo -e "${C_AZUL}admin@fedora:${C_CYAN}${DIR_PROYECTO}${C_RESET}$ cat logs/execution_metrics.json | python3 -m json.tool"
    echo ""
    cat logs/execution_metrics.json | python3 -m json.tool
    pausar_captura "Figura C3: Métricas de telemetría y Delta T" "figura_c3_metricas_telemetria.png"
}

modo_guiado() {
    echo -e "${C_VERDE}Iniciando Modo Guiado Paso a Paso...${C_RESET}"
    sleep 1
    cmd_figura_1_a2
    cmd_figura_3
    cmd_figura_4
    cmd_figura_5
    cmd_figura_b1
    cmd_figura_b2
    cmd_figura_c1
    cmd_figura_c2
    cmd_figura_c3
    cmd_figura_a1
    clear
    echo -e "${C_VERDE}¡Has completado todas las evidencias de terminal y archivos!${C_RESET}"
    echo -e "Cuando guardes las fotos en ${C_CYAN}Entregables/imagenes/${C_RESET}, ejecuta:"
    echo -e "  ${C_BLANCO}python3 scripts/build_apa_deliverable.py${C_RESET}"
    echo ""
    read -p "Presiona [ENTER] para volver al menú principal..." _
}

mostrar_menu() {
    clear
    echo -e "${C_AZUL}================================================================================${C_RESET}"
    echo -e "${C_BLANCO}     SDLC-AI: ASISTENTE INTERACTIVO DE CAPTURA DE PANTALLA REAL (ENTREGA 1)     ${C_RESET}"
    echo -e "${C_AZUL}================================================================================${C_RESET}"
    echo -e "${C_GRIS}Selecciona qué evidencia deseas proyectar en la terminal para capturarla:${C_RESET}"
    echo ""
    echo -e "  ${C_VERDE}[A]${C_RESET} ${C_BLANCO}MODO GUIADO PASO A PASO (Recorrer todas las capturas en orden)${C_RESET}"
    echo ""
    echo -e "  ${C_CYAN}[1]${C_RESET} Figura A2 / 1: Árbol de archivos y componentes (tree)"
    echo -e "  ${C_CYAN}[2]${C_RESET} Figura 3: Suite de 18 pruebas y cobertura 97% (pytest-cov docx_to_markdown)"
    echo -e "  ${C_CYAN}[3]${C_RESET} Figura 4: Dictamen Pylint 10.00/10.00 (pylint docx_to_markdown)"
    echo -e "  ${C_CYAN}[4]${C_RESET} Figura 5: Pipeline autónomo general (./run.sh - 450 SKUs, Delta T 79.04%)"
    echo -e "  ${C_CYAN}[5]${C_RESET} Figura A1: Abrir Repositorio Oficial en GitHub (Firefox)"
    echo -e "  ${C_CYAN}[6]${C_RESET} Figura B1: Manifiesto de trazabilidad JSON (conversion_manifest.json)"
    echo -e "  ${C_CYAN}[7]${C_RESET} Figura B2: Certificación de Quality Gates JSON (qa_report.json)"
    echo -e "  ${C_CYAN}[8]${C_RESET} Figura C1: Muestra del dataset sintético de retail (columnas SKU)"
    echo -e "  ${C_CYAN}[9]${C_RESET} Figura C2: Informe ejecutivo narrativo de inventarios (executive_report.md)"
    echo -e "  ${C_CYAN}[10]${C_RESET} Figura C3: Telemetría de métricas y validación Delta T (execution_metrics.json)"
    echo ""
    echo -e "  ${C_AMARILLO}[C]${C_RESET} Compilar documento DOCX y PDF una vez guardadas las imágenes reales"
    echo -e "  ${C_BLANCO}[Q]${C_RESET} Salir"
    echo -e "${C_AZUL}================================================================================${C_RESET}"
    echo -n "Selecciona una opción [A, 1-10, C, Q]: "
}

main() {
    while true; do
        mostrar_menu
        read -r opcion
        case "$opcion" in
            A|a) modo_guiado ;;
            1) cmd_figura_1_a2 ;;
            2) cmd_figura_3 ;;
            3) cmd_figura_4 ;;
            4) cmd_figura_5 ;;
            5) cmd_figura_a1 ;;
            6) cmd_figura_b1 ;;
            7) cmd_figura_b2 ;;
            8) cmd_figura_c1 ;;
            9) cmd_figura_c2 ;;
            10) cmd_figura_c3 ;;
            C|c)
                clear
                echo "Compilando documento con tus imágenes..."
                python3 scripts/build_apa_deliverable.py
                echo ""
                read -p "Presiona [ENTER] para continuar..." _
                ;;
            Q|q)
                echo "Saliendo del asistente. ¡Éxitos con las capturas!"
                exit 0
                ;;
            *)
                echo "Opción no válida."
                sleep 1
                ;;
        esac
    done
}

main
