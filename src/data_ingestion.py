"""Módulo de Ingesta y Validación de Datos de Inventario Retail.

Este módulo implementa la carga, sanitización y validación estructural de
los datos de inventario del sector retail de moda en Colombia, asegurando
que cada SKU cumpla estrictamente con la convención MODELO-TALLA-COLOR.
"""

import csv
import logging
import os
import re
from dataclasses import dataclass
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Expresión regular para validar formato MODELO-TALLA-COLOR
SKU_PATTERN = re.compile(r"^[A-Z0-9_]+-[A-Z0-9]+-[A-Z0-9]+$")


@dataclass
class InventoryItem:  # pylint: disable=too-many-instance-attributes
    """Representa una referencia de inventario por SKU y tienda."""

    sku: str
    modelo: str
    talla: str
    color: str
    categoria: str
    tienda_id: str
    ciudad: str
    stock_actual: int
    ventas_ultimos_30d: int
    precio_unitario: float


def validate_sku(sku: str) -> bool:
    """Valida si un SKU cumple con el formato MODELO-TALLA-COLOR.

    Args:
        sku: Identificador alfanumérico del producto.

    Returns:
        True si el formato es válido, False en caso contrario.
    """
    if not isinstance(sku, str):
        return False
    return bool(SKU_PATTERN.match(sku.strip()))


def parse_sku(sku: str) -> Tuple[str, str, str]:
    """Descompone un SKU válido en sus componentes modelo, talla y color.

    Args:
        sku: Identificador en formato MODELO-TALLA-COLOR.

    Returns:
        Tupla con (modelo, talla, color).

    Raises:
        ValueError: Si el SKU no cumple el formato esperado.
    """
    if not validate_sku(sku):
        raise ValueError(f"SKU inválido: '{sku}'. Debe seguir formato MODELO-TALLA-COLOR.")
    parts = sku.strip().split("-")
    return parts[0], parts[1], parts[2]


def load_inventory_csv(filepath: str) -> List[InventoryItem]:
    """Carga y valida registros de inventario desde un archivo CSV.

    Args:
        filepath: Ruta del archivo CSV a procesar.

    Returns:
        Lista de objetos InventoryItem válidos.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo carece de columnas obligatorias.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo especificado no existe: {filepath}")

    items: List[InventoryItem] = []
    discarded_count = 0
    required_columns = {
        "sku",
        "modelo",
        "talla",
        "color",
        "categoria",
        "tienda_id",
        "ciudad",
        "stock_actual",
        "ventas_ultimos_30d",
        "precio_unitario",
    }

    with open(filepath, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
            msg = f"El CSV no contiene las columnas requeridas: {required_columns}"
            raise ValueError(msg)

        for row in reader:
            try:
                sku = row["sku"].strip()
                if not validate_sku(sku):
                    discarded_count += 1
                    continue

                stock = int(row["stock_actual"])
                ventas = int(row["ventas_ultimos_30d"])
                precio = float(row["precio_unitario"])

                if stock < 0 or ventas < 0 or precio < 0:
                    discarded_count += 1
                    continue

                item = InventoryItem(
                    sku=sku,
                    modelo=row["modelo"].strip(),
                    talla=row["talla"].strip(),
                    color=row["color"].strip(),
                    categoria=row["categoria"].strip(),
                    tienda_id=row["tienda_id"].strip(),
                    ciudad=row["ciudad"].strip(),
                    stock_actual=stock,
                    ventas_ultimos_30d=ventas,
                    precio_unitario=precio,
                )
                items.append(item)
            except (ValueError, KeyError):
                discarded_count += 1
                continue

    logger.info(
        "Carga finalizada para %s: %d items válidos, %d descartados.",
        filepath,
        len(items),
        discarded_count,
    )
    return items
