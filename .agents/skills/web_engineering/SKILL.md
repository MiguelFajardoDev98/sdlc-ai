---
name: web_engineering
description: Diseña y construye sistemas web mantenibles, seguros, accesibles y comprobables.
activation: tareas con frontend, backend, APIs, autenticación, integración o despliegue web.
---

# Web engineering

## Entrada mínima
Objetivo, usuarios, plataforma, restricciones, datos, integraciones y criterio de
aceptación. Si falta seguridad, privacidad, accesibilidad o rendimiento, solicítalo
como riesgo; no lo inventes.

## Procedimiento
1. Separar interfaz, dominio, persistencia e integraciones.
2. Definir contratos HTTP/eventos, errores, validación y versionado.
3. Diseñar autenticación/autorización, gestión de secretos y límites de abuso.
4. Elegir pruebas unitarias, integración, contrato, accesibilidad y rendimiento.
5. Entregar archivos afectados, decisiones, riesgos y comandos reproducibles.

## Guardrails
No aceptar credenciales en código, entradas sin validar, autorización implícita,
errores silenciosos, HTML inaccesible ni endpoints sin pruebas de error.

## Salida
`architecture`, `contracts`, `implementation`, `tests`, `risks` y `evidence`.
