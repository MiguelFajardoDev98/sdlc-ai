---
name: python_architect
description: Habilidad especializada en diseño arquitectónico modular en Python. Aplica principios SOLID, tipado estático estricto, esquemas con Pydantic/dataclasses, diseño TDD y directrices para maximizar puntajes de Pylint y cobertura Pytest.
---

# HABILIDAD: PYTHON ARCHITECT (SDLC-AI)

Esta habilidad proporciona directrices y patrones de arquitectura de software para los agentes del framework SDLC-AI.

## 1. PRINCIPIOS DE DISEÑO Y ESTRUCTURA MODULAR
- **Single Responsibility (SRP):** Cada módulo debe concentrarse en una función única (ej. `data_ingestion.py` solo carga y valida; `kpi_calculator.py` solo computa indicadores; `alert_engine.py` solo aplica reglas de decisión).
- **Dependency Inversion (DIP):** Las dependencias externas (lectores de CSV, APIs externas) se inyectan como interfaces o clases abstractas para permitir *mocking* limpio en pruebas unitarias.
- **Tipado Estático Estricto (PEP 484):** Todas las funciones, métodos y atributos deben tener anotaciones de tipo explícitas (`int`, `float`, `str`, `List[T]`, `Dict[K, V]`, `Optional[T]`).

## 2. ESTÁNDARES DE CALIDAD Y QUALITY GATES
Para garantizar el cumplimiento de los Quality Gates del proyecto:
1. **Pylint Score >= 7.0/10.0:**
   - Todo módulo debe incluir docstring a nivel de módulo, clase y función.
   - Longitud máxima de línea: 100 caracteres.
   - Nombres de variables y funciones en snake_case descriptivo.
   - Evitar bloques `except Exception:` genéricos; capturar excepciones específicas (`FileNotFoundError`, `ValueError`, `KeyError`).
2. **Pytest Coverage >= 80%:**
   - Escribir pruebas unitarias que cubran casos felices, valores límite (frontera) y manejo de errores (ej. archivos corruptos, valores negativos o nulos).
   - Uso de `pytest.fixture` para generar datos simulados en memoria sin acoplamiento a I/O real.
3. **Manejo de Datos Tabulares:**
   - Utilizar `pandas` o estructuras nativas tipadas (`dataclasses`) con validación de tipos antes de proceder al cómputo de métricas.
