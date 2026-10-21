"""Lector y extractor semántico de documentos DOCX (Open XML / OOXML)."""

import hashlib
import zipfile
from pathlib import Path
from typing import List, Optional, Protocol, Tuple

import docx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from docx_to_markdown.exceptions import DocumentNotFoundError, InvalidDocxError
from docx_to_markdown.models import (
    ConversionConfig,
    DocumentElement,
    ElementType,
    ExtractedImage,
)

HEADING_PREFIXES: Tuple[str, ...] = ("heading", "título", "titulo")
LIST_PREFIXES: Tuple[str, ...] = ("list", "lista")
MONOSPACE_FONTS: Tuple[str, ...] = ("consolas", "courier new", "courier", "monospace")


class IDocumentReader(Protocol):  # pylint: disable=too-few-public-methods
    """Protocolo abstracto que define el contrato de lectura de documentos."""

    def read(  # pylint: disable=too-many-locals,protected-access
        self, file_path: Path, config: Optional[ConversionConfig] = None
    ) -> List[DocumentElement]:
        """Extrae la secuencia ordenada de elementos del documento."""
        ...


class DocxReader:
    """Implementación de IDocumentReader para archivos Microsoft Word (.docx)."""

    def validate_file(self, file_path: Path) -> None:
        """Verifica la existencia y validez estructural del archivo DOCX.

        Args:
            file_path: Ruta al archivo a validar.

        Raises:
            DocumentNotFoundError: Si el archivo no existe.
            InvalidDocxError: Si el archivo no es un ZIP/OOXML válido.
        """
        if not file_path.exists() or file_path.is_dir():
            raise DocumentNotFoundError(f"Documento no encontrado o es directorio: {file_path}")

        if not zipfile.is_zipfile(file_path):
            raise InvalidDocxError(f"El archivo no es un paquete OOXML/ZIP válido: {file_path}")

        try:
            with zipfile.ZipFile(file_path, "r") as archive:
                namelist = archive.namelist()
                if "word/document.xml" not in namelist:
                    raise InvalidDocxError(
                        f"Falta 'word/document.xml' en el contenedor OOXML: {file_path}"
                    )
        except zipfile.BadZipFile as exc:
            raise InvalidDocxError(f"Archivo DOCX corrupto: {exc}") from exc

    def _parse_inline_runs(self, paragraph: Paragraph) -> str:
        """Parsea los runs de un párrafo traduciendo estilos inline a Markdown.

        Args:
            paragraph: Párrafo de python-docx.

        Returns:
            Texto con marcado inline (negrita, cursiva, código).
        """
        parts: List[str] = []
        for run in paragraph.runs:
            text = run.text
            if not text:
                continue

            # Preservar espacios alrededor del formato para sintaxis Markdown válida
            leading_space = " " if text.startswith(" ") and len(text.strip()) > 0 else ""
            trailing_space = " " if text.endswith(" ") and len(text.strip()) > 0 else ""
            clean_text = text.strip()

            if not clean_text:
                parts.append(text)
                continue

            is_code = False
            font_name = run.font.name.lower() if run.font and run.font.name else ""
            if any(mono in font_name for mono in MONOSPACE_FONTS):
                clean_text = f"`{clean_text}`"
                is_code = True

            if run.bold and not is_code:
                clean_text = f"**{clean_text}**"

            if run.italic and not is_code:
                clean_text = f"*{clean_text}*"

            parts.append(f"{leading_space}{clean_text}{trailing_space}")

        return "".join(parts)

    def _extract_images_from_paragraph(  # pylint: disable=too-many-locals,protected-access
        self,
        paragraph: Paragraph,
        doc: docx.Document,
        image_counter: int,
        config: ConversionConfig,
    ) -> List[ExtractedImage]:
        """Extrae imágenes incrustadas dentro de un párrafo."""
        if not config.extract_images:
            return []

        images: List[ExtractedImage] = []
        blips = paragraph._p.xpath(".//a:blip")
        for blip in blips:
            r_id = blip.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
            )
            if not r_id or r_id not in doc.part.related_parts:
                continue

            part = doc.part.related_parts[r_id]
            blob_bytes: bytes = part.blob
            ext = part.content_type.split("/")[-1]
            if ext == "jpeg":
                ext = "jpg"

            filename = f"img_{image_counter:03d}.{ext}"
            rel_path = f"{config.assets_dir_name}/{filename}"
            sha256 = hashlib.sha256(blob_bytes).hexdigest()

            # Buscar texto alternativo en docPr si existe
            alt_text = ""
            doc_prs = paragraph._p.xpath(".//wp:docPr")
            if doc_prs:
                alt_text = doc_prs[0].get("descr") or doc_prs[0].get("name") or ""

            images.append(
                ExtractedImage(
                    filename=filename,
                    data=blob_bytes,
                    rel_path=rel_path,
                    sha256=sha256,
                    alt_text=alt_text,
                )
            )
        return images

    def _get_heading_level(self, style_name: str) -> Optional[int]:
        """Determina si un estilo corresponde a un encabezado y su nivel (1-6)."""
        lower_name = style_name.lower().strip()
        for prefix in HEADING_PREFIXES:
            if lower_name.startswith(prefix):
                suffix = lower_name[len(prefix):].strip()
                if suffix.isdigit():
                    level = int(suffix)
                    return max(1, min(6, level))
        return None

    def _is_list_item(self, paragraph: Paragraph) -> Tuple[bool, bool, int]:
        """Detecta si el párrafo es elemento de lista (is_list, is_ordered, level)."""
        # pylint: disable=protected-access
        style_name = paragraph.style.name.lower() if paragraph.style else ""
        num_pr = paragraph._p.xpath("./w:pPr/w:numPr")
        if num_pr:
            ilvl_elem = paragraph._p.xpath("./w:pPr/w:numPr/w:ilvl")
            level = int(ilvl_elem[0].get(qn("w:val"), 0)) if ilvl_elem else 0
            is_bullet = "bullet" in style_name
            return True, not is_bullet, level

        if any(style_name.startswith(p) for p in LIST_PREFIXES):
            is_ordered = "number" in style_name or "número" in style_name
            return True, is_ordered, 0

        return False, False, 0

    def read(  # pylint: disable=too-many-locals,protected-access
        self, file_path: Path, config: Optional[ConversionConfig] = None
    ) -> List[DocumentElement]:
        """Lee el documento DOCX y extrae sus elementos semánticos secuenciales.

        Args:
            file_path: Ruta al archivo DOCX.
            config: Opciones de configuración.

        Returns:
            Lista de DocumentElement en orden estricto de aparición.
        """
        cfg = config or ConversionConfig()
        self.validate_file(file_path)

        doc = docx.Document(str(file_path))
        elements: List[DocumentElement] = []
        image_counter = 1

        for child in doc.element.body:
            tag = child.tag.split("}")[-1]

            if tag == "p":
                paragraph = Paragraph(child, doc)
                text = paragraph.text.strip()

                # Extracción de imágenes
                images = self._extract_images_from_paragraph(
                    paragraph, doc, image_counter, cfg
                )
                for img in images:
                    elements.append(
                        DocumentElement(
                            element_type=ElementType.IMAGE,
                            content=img,
                            metadata={"filename": img.filename},
                        )
                    )
                    image_counter += 1

                # Elementos no soportados (SmartArt / Objetos OLE)
                if paragraph._p.xpath(".//w:object") or paragraph._p.xpath(".//dgm:*"):
                    elements.append(
                        DocumentElement(
                            element_type=ElementType.UNSUPPORTED,
                            content="Objeto OLE o Diagrama SmartArt",
                            metadata={"type": "OLE/SmartArt"},
                        )
                    )

                if not text and cfg.ignore_empty_paragraphs:
                    continue

                style_name = paragraph.style.name if paragraph.style else "Normal"
                heading_level = self._get_heading_level(style_name)

                if heading_level is not None:
                    elements.append(
                        DocumentElement(
                            element_type=ElementType.HEADING,
                            content=text,
                            level=heading_level,
                            metadata={"style": style_name},
                        )
                    )
                    continue

                is_list, is_ordered, list_level = self._is_list_item(paragraph)
                if is_list:
                    formatted_text = self._parse_inline_runs(paragraph) or text
                    elements.append(
                        DocumentElement(
                            element_type=ElementType.LIST_ITEM,
                            content=formatted_text,
                            level=list_level,
                            metadata={"ordered": is_ordered, "style": style_name},
                        )
                    )
                    continue

                # Párrafo normal
                formatted_text = self._parse_inline_runs(paragraph) or text
                elements.append(
                    DocumentElement(
                        element_type=ElementType.PARAGRAPH,
                        content=formatted_text,
                        metadata={"style": style_name},
                    )
                )

            elif tag == "tbl":
                table = Table(child, doc)
                table_matrix: List[List[str]] = []
                for row in table.rows:
                    row_cells: List[str] = []
                    for cell in row.cells:
                        # Extraer texto de la celda normalizando saltos internos
                        cell_text = cell.text.strip()
                        row_cells.append(cell_text)
                    table_matrix.append(row_cells)

                if table_matrix:
                    elements.append(
                        DocumentElement(
                            element_type=ElementType.TABLE,
                            content=table_matrix,
                            metadata={
                                "rows": len(table_matrix),
                                "cols": len(table_matrix[0]) if table_matrix else 0,
                            },
                        )
                    )

        return elements
