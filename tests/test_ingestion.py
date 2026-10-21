"""Pruebas unitarias para el módulo de ingesta de datos de inventario."""

import os
import tempfile
import pytest
from src.data_ingestion import (
    InventoryItem,
    validate_sku,
    parse_sku,
    load_inventory_csv,
)


def test_validate_sku_valid():
    """Verifica que SKUs con formato MODELO-TALLA-COLOR sean aceptados."""
    assert validate_sku("CAMISA_OXFORD-M-AZUL") is True
    assert validate_sku("JEAN_SLIM-32-INDIGO") is True
    assert validate_sku("POLO_PIQUE-S-BLANCO") is True
    assert validate_sku("VESTIDO_SEDA-L-ROJO") is True


def test_validate_sku_invalid():
    """Verifica que SKUs con formato no estándar sean rechazados."""
    assert validate_sku("CAMISA-AZUL") is False
    assert validate_sku("camisa_oxford-m-azul") is False
    assert validate_sku("") is False
    assert validate_sku("SKU_SIN_GUIONES") is False
    assert validate_sku(12345) is False


def test_parse_sku_success():
    """Verifica la descomposición correcta de componentes del SKU."""
    modelo, talla, color = parse_sku("BLUSA_LINO-XS-CORAL")
    assert modelo == "BLUSA_LINO"
    assert talla == "XS"
    assert color == "CORAL"


def test_parse_sku_failure():
    """Verifica que se lance ValueError ante un SKU inválido."""
    with pytest.raises(ValueError):
        parse_sku("INVALID_FORMAT")


def test_load_inventory_csv_success():
    """Verifica la carga exitosa del archivo sintético generado."""
    filepath = "data/synthetic_retail_data.csv"
    items = load_inventory_csv(filepath)
    assert len(items) == 450
    assert all(isinstance(item, InventoryItem) for item in items)
    assert all(validate_sku(item.sku) for item in items)


def test_load_inventory_csv_not_found():
    """Verifica que se lance FileNotFoundError si el archivo no existe."""
    with pytest.raises(FileNotFoundError):
        load_inventory_csv("data/archivo_inexistente.csv")


def test_load_inventory_csv_discard_invalid_rows():
    """Verifica el descarte de filas con datos corruptos o valores negativos."""
    csv_content = (
        "sku,modelo,talla,color,categoria,tienda_id,ciudad,stock_actual,ventas_ultimos_30d,precio_unitario\n"
        "CAMISA_OXFORD-M-AZUL,CAMISA_OXFORD,M,AZUL,Hombre,T001,Bogotá,10,20,120000\n"
        "SKU_INVALIDO,CAMISA_OXFORD,M,AZUL,Hombre,T001,Bogotá,10,20,120000\n"
        "JEAN_SLIM-32-AZUL,JEAN_SLIM,32,AZUL,Hombre,T001,Bogotá,-5,20,140000\n"
    )
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tmp:
        tmp.write(csv_content)
        tmp_path = tmp.name

    try:
        items = load_inventory_csv(tmp_path)
        assert len(items) == 1
        assert items[0].sku == "CAMISA_OXFORD-M-AZUL"
    finally:
        os.remove(tmp_path)
