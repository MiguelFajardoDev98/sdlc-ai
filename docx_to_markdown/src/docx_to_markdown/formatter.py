"""Formateador de sintaxis GitHub Flavored Markdown (GFM) a partir de AST de elementos."""

from typing import List, Tuple

from docx_to_markdown.models import (
    ConversionConfig,
    DocumentElement,
    ElementStats,
    ElementType,
    ExtractedImage,
)


class MarkdownFormatter:
    """Transforma una secuencia de DocumentElement en texto Markdown normalizado UTF-8."""

    def __init__(self, config: ConversionConfig) -> None:
        """Inicializa el formateador con la configuración especificada.

        Args:
            config: Configuración de conversión.
        """
        self._config = config

    def format_heading(self, text: str, level: int) -> str:
        """Formatea un encabezado Markdown con el nivel correspondiente (# a ######)."""
        clamped_level = max(1, min(6, level))
        prefix = "#" * clamped_level
        return f"{prefix} {text}"

    def format_paragraph(self, text: str) -> str:
        """Formatea un párrafo de texto ordinario."""
        return text

    def format_list_item(
        self, text: str, level: int, is_ordered: bool, index: int = 1
    ) -> str:
        """Formatea un elemento de lista simple o anidada."""
        indent = "  " * max(0, level)
        marker = f"{index}. " if is_ordered else "- "
        return f"{indent}{marker}{text}"

    def format_table(self, rows: List[List[str]]) -> str:
        """Formatea una matriz de datos en una tabla sintácticamente válida en GFM.

        Args:
            rows: Matriz bidimensional de celdas de texto.

        Returns:
            Cadena con la tabla formateada en GFM.
        """
        if not rows:
            return ""

        # Determinar número máximo de columnas
        max_cols = max(len(row) for row in rows)
        if max_cols == 0:
            return ""

        formatted_lines: List[str] = []

        def clean_cell(cell_value: str) -> str:
            # Reemplazar saltos de línea y escapar barras verticales
            clean = cell_value.replace("|", r"\|")
            clean = clean.replace("\r\n", "\n").replace("\r", "\n")
            clean = clean.replace("\n", self._config.table_cell_linebreak_replacement)
            return clean.strip()

        # Fila de cabecera
        header_row = rows[0]
        padded_header = [
            clean_cell(header_row[i]) if i < len(header_row) else ""
            for i in range(max_cols)
        ]
        formatted_lines.append(f"| {' | '.join(padded_header)} |")

        # Fila separadora obligatoria en GFM
        separator = ["---"] * max_cols
        formatted_lines.append(f"| {' | '.join(separator)} |")

        # Filas de datos
        for row in rows[1:]:
            padded_row = [
                clean_cell(row[i]) if i < len(row) else ""
                for i in range(max_cols)
            ]
            formatted_lines.append(f"| {' | '.join(padded_row)} |")

        return "\n".join(formatted_lines)

    def format_image(self, image: ExtractedImage) -> str:
        """Genera el enlace Markdown relativo a una imagen extraída."""
        alt = image.alt_text if image.alt_text else image.filename
        return f"![{alt}]({image.rel_path})"

    def format_elements(
        self, elements: List[DocumentElement]
    ) -> Tuple[str, List[str], ElementStats]:
        """Procesa y formatea la colección completa de elementos en un documento Markdown.

        Args:
            elements: Lista de elementos en orden secuencial.

        Returns:
            Tupla de (markdown_completo, lista_advertencias, estadisticas).
        """
        markdown_blocks: List[str] = []
        warnings: List[str] = []
        stats = ElementStats()

        list_counter = 1
        previous_was_ordered_list = False

        for element in elements:
            if element.element_type == ElementType.HEADING:
                stats.headings_by_level[element.level] = (
                    stats.headings_by_level.get(element.level, 0) + 1
                )
                markdown_blocks.append(self.format_heading(str(element.content), element.level))
                previous_was_ordered_list = False

            elif element.element_type == ElementType.PARAGRAPH:
                stats.paragraphs += 1
                markdown_blocks.append(self.format_paragraph(str(element.content)))
                previous_was_ordered_list = False

            elif element.element_type == ElementType.LIST_ITEM:
                is_ordered = bool(element.metadata.get("ordered", False))
                if is_ordered:
                    if not previous_was_ordered_list:
                        list_counter = 1
                    item_str = self.format_list_item(
                        str(element.content), element.level, is_ordered=True, index=list_counter
                    )
                    list_counter += 1
                    previous_was_ordered_list = True
                else:
                    item_str = self.format_list_item(
                        str(element.content), element.level, is_ordered=False
                    )
                    previous_was_ordered_list = False

                stats.paragraphs += 1
                markdown_blocks.append(item_str)

            elif element.element_type == ElementType.TABLE:
                stats.tables += 1
                table_matrix: List[List[str]] = element.content
                stats.table_cells += sum(len(row) for row in table_matrix)
                markdown_blocks.append(self.format_table(table_matrix))
                previous_was_ordered_list = False

            elif element.element_type == ElementType.IMAGE:
                stats.images += 1
                img: ExtractedImage = element.content
                markdown_blocks.append(self.format_image(img))
                previous_was_ordered_list = False

            elif element.element_type == ElementType.UNSUPPORTED:
                warn_msg = f"Elemento no representable omitido: {element.content}"
                warnings.append(warn_msg)
                marker = f"<!-- WARNING: {warn_msg} -->"
                markdown_blocks.append(marker)
                previous_was_ordered_list = False

        # Unir bloques con doble salto de línea estándar
        full_markdown = "\n\n".join(markdown_blocks).strip() + "\n"
        return full_markdown, warnings, stats
