---
title: |
  SDLC-AI: Framework de Inteligencia Artificial Agéntica  
  para el Ciclo de Vida del Desarrollo de Software

  **Caso de Estudio:** Sistema de Alertas de Inventario  
  para el Sector Retail de Moda en Colombia
author: "Miguel Ángel Fajardo Cossio  \nC.C. 1234990751"
date: "Septiembre de 2026"
---

# DATOS GENERALES --- PROYECTO DE GRADO

  -----------------------------------------------------------------------
  **Facultad**              Ingeniería y Ciencias Básicas
  ------------------------- ---------------------------------------------
  **Departamento            Ingeniería de Software
  Académico**               

  **Nombre completo**       Miguel Ángel Fajardo Cossio

  **Cédula No.**            1234990751

  **Correo electrónico**    manfajardoc@poligran.edu.co

  **Asesor**                Wilson Eduardo Soto Forero

  **Título del              SDLC-AI: Framework de Inteligencia Artificial
  anteproyecto**            Agéntica para el Ciclo de Vida del Desarrollo
                            de Software --- Caso de Estudio: Sistema de
                            Alertas de Inventario para el Sector Retail
                            de Moda en Colombia

  **Área de conocimiento**  Inteligencia Artificial, Ingeniería de
                            Software, Analítica de Datos Retail

  **Palabras clave**        IA agéntica, framework SDLC-AI, orquestación
                            multi-agente, ciclo de vida del software,
                            Gemini Pro, Python, evaluación comparativa,
                            automatización, retail (caso de estudio)

  **Fecha de inicio**       5 de septiembre de 2026

  **Fecha de finalización** 15 de diciembre de 2026

  **Tipo de trabajo**       Proyecto de Grado --- Investigativo y
                            Aplicado
  -----------------------------------------------------------------------

# RESUMEN

El presente proyecto de grado propone el diseño, implementación y
evaluación del framework **SDLC-AI**, un sistema de orquestación de
agentes de Inteligencia Artificial Agéntica que automatiza las fases del
Ciclo de Vida del Desarrollo de Software (SDLC): análisis de requisitos,
diseño y arquitectura, desarrollo, pruebas y despliegue. El framework se
valida mediante la construcción de un sistema de alertas de inventario
para el sector retail de moda en Colombia como caso de estudio.

A diferencia de propuestas que aplican IA de forma puntual en fases
aisladas, SDLC-AI propone una arquitectura de cinco roles agénticos
especializados y coordinados: un Agente Analista, un Agente Auditor de
Especificaciones, un Agente Arquitecto, un Agente Desarrollador, un
Agente Tester y un Agente DevOps. El proceso se estructura en dos etapas
diferenciadas por el nivel de intervención humana: una **Fase de
Especificación Asistida**, donde el investigador colabora activamente
con los agentes analista y auditor para producir una especificación
completa, rigurosa y sin ambigüedades; y un **Pipeline de Ejecución
Autónoma**, donde los agentes de diseño, desarrollo, pruebas y
despliegue operan de forma encadenada sin requerir intervención humana
adicional. Este modelo de especificación front-loaded minimiza el
retrabajo y el consumo de recursos computacionales en las fases de
ejecución.

La evaluación del framework se realiza mediante métricas cuantitativas
---tiempo de desarrollo por fase, calidad estática del código (pylint
score), cobertura de pruebas (pytest-cov) y precisión de alertas
(F1-score)--- comparadas contra una línea base de estimación paramétrica
de esfuerzo de desarrollo tradicional equivalente. Se espera demostrar
que el enfoque SDLC-AI reduce significativamente los tiempos de
desarrollo manteniendo estándares de calidad aceptables, estableciendo
así un modelo de referencia replicable en contextos donde la velocidad
de construcción de software analítico sea un factor crítico.

**Palabras clave:** inteligencia artificial agéntica, framework SDLC-AI,
orquestación multi-agente, ciclo de vida del software, especificación
front-loaded, evaluación comparativa, Google Gemini Pro, Python,
automatización, retail.

# 1. INTRODUCCIÓN

El proyecto SDLC-AI surge de la convergencia entre dos campos de alta
relevancia contemporánea: la Inteligencia Artificial Generativa y la
Ingeniería de Software aplicada al sector empresarial. En particular, el
proyecto se enfoca en explorar cómo los agentes de inteligencia
artificial ---entidades autónomas capaces de razonar, planificar y
actuar sobre su entorno--- pueden asumir roles específicos dentro del
proceso clásico de desarrollo de software, reduciendo la brecha entre la
concepción de una solución tecnológica y su puesta en producción.

El sector retail de moda en Colombia enfrenta desafíos logísticos y
analíticos que demandan soluciones de software ágiles y precisas. Sin
embargo, el desarrollo tradicional de estas soluciones es lento, costoso
y frecuentemente desconectado de las necesidades cambiantes del negocio.
La propuesta de este trabajo de grado es demostrar que un pipeline de
agentes inteligentes, orquestado con Python y Google Gemini Pro, puede
automatizar las fases del SDLC para producir, en menor tiempo y con
mayor trazabilidad, un sistema de alertas tempranas orientado a la
gestión de inventarios y distribución de producto.

Este documento constituye el Anteproyecto del proyecto de grado, y
comprende el planteamiento del problema, los objetivos, la
justificación, la revisión de literatura inicial, la metodología
propuesta y el cronograma de trabajo para los cuatro meses de duración
del proyecto académico.

## 1.1 Planteamiento del Problema

El sector retail de moda en Colombia opera en un entorno de alta
variabilidad donde la velocidad de las tendencias de consumo, la
estacionalidad y la dispersión geográfica de los puntos de venta generan
complejidades significativas en la gestión de inventarios. Empresas de
este sector se enfrentan cotidianamente a la pregunta: ¿cómo garantizar
que el producto correcto esté disponible en la tienda correcta en el
momento adecuado, al menor costo operativo posible?

La identificación tardía de quiebres de stock, el exceso de inventario
en referencias de baja rotación y la incapacidad para detectar
oportunamente el surgimiento de nuevas tendencias de demanda son
manifestaciones concretas de este problema. Estas situaciones generan
pérdidas directas en ventas, incrementan los costos de transferencia
entre tiendas y deterioran la experiencia del cliente final (Chopra & Meindl, 2022).

Desde la perspectiva de la Ingeniería de Software, construir soluciones
analíticas que aborden estos retos de manera oportuna enfrenta un
problema adicional: el tiempo de desarrollo de software es, por sí
mismo, una limitación. Los ciclos tradicionales de análisis, diseño,
codificación y pruebas pueden tardar semanas o meses, tiempo durante el
cual el contexto del negocio ya ha cambiado (Pressman & Maxim, 2021).

Esta doble problemática ---operativa en el retail y metodológica en el
desarrollo de software--- plantea la siguiente pregunta de
investigación:

> ***¿En qué medida el framework de orquestación de agentes autónomos
> SDLC-AI reduce el tiempo de desarrollo y mejora la calidad del código
> producido ---medida por pylint score y cobertura de pruebas--- en
> comparación con la estimación de esfuerzo de un desarrollo tradicional
> equivalente, al construir un sistema de alertas de inventario para el
> sector retail de moda en Colombia?***

Las fuentes bibliográficas que sustentan el marco del problema incluyen
investigaciones recientes sobre IA agéntica (Wang et al., 2024), gestión de
inventarios en retail (Chopra & Meindl, 2022) y evaluación de metodologías ágiles en
contextos latinoamericanos (Kuhrmann et al., 2022).

## 1.2 Justificación

La relevancia de este proyecto se articula en tres dimensiones
fundamentales: tecnológica, disciplinar y sectorial.

**Desde la perspectiva tecnológica,** la emergencia de los Large
Language Models (LLM) y, en particular, de arquitecturas multiagente
capaces de razonar en cadena (Chain-of-Thought) y de ejecutar acciones
sobre herramientas externas (Tool Use), representa un cambio de
paradigma en la forma en que se concibe el desarrollo de software.
Google Gemini Pro, con sus capacidades de razonamiento multimodal y su
integración nativa con herramientas de código mediante la librería
Antigravity, ofrece un ecosistema ideal para explorar estas
posibilidades (Gemini Team et al., 2024). Investigar y documentar cómo estas capacidades se
aplican en un contexto de ingeniería real constituye una contribución
valiosa al estado del arte en la disciplina.

**Desde la perspectiva de la Ingeniería de Software,** este proyecto
aborda directamente una de las problemáticas más persistentes del campo:
la brecha entre la velocidad de cambio del negocio y la velocidad de
respuesta del desarrollo de software. Al proponer que agentes de IA
asuman roles funcionales dentro del SDLC ---levantamiento de requisitos,
diseño, codificación, pruebas y despliegue---, el proyecto explora un
nuevo modelo de ingeniería aumentada por IA que puede tener
implicaciones profundas en la productividad y en la naturaleza misma del
rol del ingeniero de software (Hong et al., 2024; Qian et al., 2024).

**Desde la perspectiva del sector retail colombiano,** la necesidad de
soluciones analíticas oportunas y costo-eficientes es urgente. El
comercio de moda en Colombia representa un sector con alta informalidad,
márgenes ajustados y alta competencia, donde la inteligencia operativa
basada en datos puede ser un factor diferenciador determinante (Ferreira et al., 2016; Inexmoda, 2024). Un
sistema de alertas tempranas de inventario, construido de forma
eficiente mediante agentes IA, tiene el potencial de generar impacto
económico real en empresas pequeñas y medianas que no cuentan con los
recursos para contratar equipos de desarrollo de software extensos.

En síntesis, este trabajo de grado es pertinente porque responde a
necesidades reales del sector empresarial colombiano, contribuye al
avance disciplinar en Ingeniería de Software y explora de manera
rigurosa y documentada las fronteras actuales de la IA aplicada (Kuhrmann et al., 2022).

## 1.3 Alcance

**El proyecto incluye:**

- El diseño e implementación del framework SDLC-AI, con cinco roles
  agénticos definidos y orquestados en Python.

- El desarrollo de un sistema de alertas tempranas de abastecimiento e
  inventario como caso de uso de aplicación del framework.

- La evaluación cualitativa y cuantitativa del proceso de desarrollo
  mediado por agentes IA, en comparación con el enfoque tradicional.

- La documentación completa del proceso, los aprendizajes y las
  directrices replicables.

**El proyecto excluye:**

- Integraciones directas con sistemas ERP o bases de datos empresariales
  propietarias.

- El despliegue en entornos de producción empresarial real (el
  despliegue será en entorno académico controlado).

- El análisis de otras verticales del retail distintas al sector de
  moda.

- El entrenamiento de modelos de lenguaje propios; el proyecto utiliza
  la API de Google Gemini Pro como servicio.

## 1.4 Objetivo General

Diseñar, implementar y evaluar el framework **SDLC-AI**, un sistema de
orquestación de agentes de Inteligencia Artificial Agéntica que
automatiza las fases del Ciclo de Vida del Desarrollo de Software (SDLC)
---análisis, diseño, desarrollo, pruebas y despliegue---, midiendo
mediante métricas cuantitativas su impacto en la reducción de tiempos de
desarrollo y la calidad del código producido con respecto a una
estimación de desarrollo tradicional equivalente, a través de la
construcción de un sistema de alertas de inventario para el sector
retail de moda en Colombia como caso de estudio.

## 1.5 Objetivos Específicos

**1. Diseñar la arquitectura del framework SDLC-AI**, definiendo los
roles agénticos, el protocolo de orquestación entre agentes, los
mecanismos de comunicación de estado y los puntos de intervención humana
en la Fase de Especificación Asistida.

**2. Producir la especificación completa y auditada del caso de
estudio**, mediante la colaboración del investigador con el Agente
Analista y el Agente Auditor de Especificaciones, generando un Documento
de Requisitos (SRS) libre de ambigüedades que sirva como entrada única
al pipeline de ejecución autónoma.

**3. Ejecutar el pipeline de diseño y desarrollo de forma autónoma**,
donde el Agente Arquitecto genera el diseño técnico (TDD) y el Agente
Desarrollador produce el código fuente del sistema de alertas a partir
exclusivamente de la especificación aprobada, sin intervención humana
adicional.

**4. Validar la solución de forma autónoma**, mediante el Agente Tester
que ejecuta pruebas unitarias e integradas, mide la cobertura de código
y la precisión de alertas, y coordina con el Agente Desarrollador las
correcciones necesarias hasta superar los umbrales de calidad definidos.

**5. Comparar cuantitativamente** los tiempos de desarrollo y métricas
de calidad del pipeline SDLC-AI contra la línea base de estimación
paramétrica tradicional, identificando el impacto del modelo de
especificación front-loaded sobre la eficiencia del pipeline autónomo.

# 2. REVISIÓN DE LITERATURA Y ANTECEDENTES

Este apartado presenta los fundamentos teóricos y antecedentes de
investigación que enmarcan el proyecto SDLC-AI. El objetivo no es una
exposición exhaustiva de definiciones formales, sino mostrar cómo los
conceptos clave se articulan con el problema de estudio y justifican las
decisiones metodológicas adoptadas.

## 2.1 Inteligencia Artificial Agéntica

La Inteligencia Artificial Agéntica se refiere a sistemas de IA capaces
de percibir su entorno, tomar decisiones autónomas y ejecutar acciones
encadenadas para alcanzar objetivos definidos, sin requerir intervención
humana en cada paso del proceso. A diferencia de los modelos de lenguaje
utilizados de forma puramente conversacional, los agentes de IA integran
capacidades de razonamiento (Chain-of-Thought Prompting), planificación
(ReAct, Plan-and-Execute) y uso de herramientas externas (Tool Use,
Function Calling) para operar de manera autónoma sobre tareas complejas
y de múltiples pasos (Wang et al., 2024).

En el contexto del desarrollo de software, un agente de IA puede ser
instruido para asumir un rol específico ---analista, arquitecto,
programador, tester--- y ejecutar las tareas propias de ese rol
utilizando herramientas como editores de código, compiladores, motores
de búsqueda o APIs de terceros. La investigación reciente, como los
trabajos sobre ChatDev (Qian et al., 2024) y MetaGPT (Hong et al., 2024), ha demostrado que la
orquestación de múltiples agentes especializados puede producir software
funcional a partir de descripciones de alto nivel, aunque aún con
limitaciones en la gestión de proyectos de mayor complejidad.

## 2.2 Ecosistema Google Gemini Pro

Google Gemini Pro es un modelo de lenguaje grande (LLM) de la familia
Gemini, desarrollado por Google DeepMind, con capacidades de
razonamiento multimodal (texto, código, imágenes y datos estructurados).
Sus características principales relevantes para este proyecto incluyen
(Gemini Team et al., 2024):

- Contexto extendido: ventanas de contexto de hasta un millón de tokens,
  lo que permite procesar documentos extensos de requisitos o bases de
  código completas en una sola interacción.

- Function Calling nativo: capacidad de invocar funciones y herramientas
  externas de forma estructurada, fundamental para la autonomía de los
  agentes.

- Razonamiento estructurado: capacidad para producir salidas en formatos
  estructurados (JSON, Python) con alta fiabilidad, esencial para la
  generación de código.

- API accesible: disponible mediante Google AI Studio y la SDK oficial
  de Python, facilitando la integración en pipelines de desarrollo.

## 2.3 Antigravity CLI y Librería Python

Antigravity es una herramienta de asistencia en el desarrollo de
software potenciada por modelos de lenguaje de Google, que opera tanto
como interfaz de línea de comandos (CLI) como librería de Python. En el
contexto de este proyecto, Antigravity actúa como la capa de
orquestación que permite a los agentes:

- Interactuar con el sistema de archivos del proyecto de forma segura y
  estructurada.

- Ejecutar comandos de sistema y scripts de Python en el contexto del
  proyecto.

- Gestionar el contexto conversacional de cada agente, manteniendo la
  coherencia entre las diferentes fases del SDLC.

- Aplicar skills especializadas que condicionan el comportamiento de
  cada agente según su rol (retail_strategist, python_architect).

La integración de Antigravity como capa de orquestación representa una
aproximación pragmática y replicable al concepto de IA agéntica aplicada
al desarrollo de software, dado que combina las capacidades de los LLM
con herramientas concretas del entorno de desarrollo.

## 2.4 Ciclo de Vida del Desarrollo de Software (SDLC)

El Ciclo de Vida del Desarrollo de Software es el marco estructural que
define las fases, actividades, roles y entregables del proceso de
construcción de software. Las metodologías tradicionales (Waterfall,
Spiral) y ágiles (Scrum, Kanban) proponen diferentes formas de organizar
estas fases, pero comparten un conjunto de actividades fundamentales:
análisis de requisitos, diseño, implementación, pruebas y despliegue
(Pressman & Maxim, 2021).

En el contexto de SDLC-AI, cada una de estas fases es abordada por un
agente especializado que utiliza Gemini Pro como motor de razonamiento y
Antigravity como capa de ejecución. Este enfoque no busca reemplazar al
ingeniero de software, sino aumentar su capacidad de producción y
reducir el tiempo de ciclo mediante la automatización de tareas
repetitivas y de alto volumen cognitivo.

## 2.5 Dominio de Aplicación: Alertas de Inventario en el Sector Retail

El sector retail de moda en Colombia constituye el **dominio de
validación** del framework SDLC-AI. Su elección como caso de estudio se
justifica por la combinación de alta complejidad operativa y la
disponibilidad de datos estructurables para pruebas. No es el objeto de
investigación primario del proyecto, sino el contexto real sobre el cual
se demuestra que el framework puede producir software funcional y
evaluable.

La gestión de inventarios en el sector retail de moda presenta
características particulares que la distinguen de otros sectores
industriales: alta volatilidad de la demanda, ciclos de producto cortos,
alta fragmentación por talla y color (SKU), y la necesidad de
distribución eficiente entre múltiples puntos de venta (Chopra & Meindl,
2022). Los sistemas de alerta temprana de inventario son herramientas
analíticas que monitorizan indicadores como el nivel de servicio, la
cobertura de inventario y la tasa de quiebre, generando alertas cuando
estos indicadores se aproximan a umbrales críticos.

La integración de IA en la gestión de inventarios retail es un campo en
crecimiento, con aplicaciones que van desde la predicción de demanda
basada en series temporales hasta la optimización de la distribución
mediante algoritmos de asignación (Ferreira et al., 2016). El aporte de
este proyecto a este campo es indirecto: demuestra que un framework de
agentes IA puede construir el software analítico de forma más eficiente
que un equipo de desarrollo tradicional, democratizando el acceso a
estas herramientas en el contexto de pequeñas y medianas empresas del
sector.

# 3. METODOLOGÍA PROPUESTA

## 3.1 Enfoque de Investigación

El proyecto adopta un enfoque de investigación aplicada con diseño
iterativo e incremental. La investigación aplicada implica que el
objetivo central no es la generación de teoría abstracta, sino la
solución de un problema concreto: la optimización del proceso de
desarrollo de software y la gestión de inventarios en retail. El objeto
de investigación es el framework SDLC-AI; el dominio de aplicación es el
sistema de alertas de inventario para retail, que actúa como caso de
estudio para validar el framework. El diseño iterativo e incremental
organiza el desarrollo del caso de estudio en cuatro Sprints funcionales,
donde cada Sprint produce un incremento evaluable que alimenta al
siguiente.

Desde la perspectiva de la metodología de investigación, el proyecto
utiliza:

- **Datos primarios:** generados directamente durante el proceso de
  desarrollo mediado por agentes IA, incluyendo trazas de conversación,
  timestamps de ejecución por fase, métricas de calidad del código y
  registros de las decisiones del Agente Auditor durante la Fase de
  Especificación.

- **Datos secundarios:** literatura académica y técnica sobre IA
  agéntica, gestión de inventarios retail y metodologías de desarrollo
  de software.

- **Técnicas de recolección:** registro sistemático de artefactos y logs
  de cada agente, análisis de métricas con herramientas automatizadas
  (pylint, pytest-cov) y evaluación comparativa contra la línea base
  paramétrica.

### 3.1.1 Línea Base de Comparación

Para posibilitar la comparación cuantitativa entre el enfoque SDLC-AI y
el desarrollo tradicional, se establece una **línea base mediante
estimación paramétrica** del esfuerzo requerido para construir el
sistema de alertas de inventario. Esta estimación se construirá al
inicio del proyecto, descomponiendo el sistema en unidades funcionales
valoradas en puntos de historia ($PH$) según la escala Fibonacci (1, 2, 3, 5,
8, 13). Se aplicará una velocidad de referencia de 10 puntos por
semana-programador, derivada de la literatura sobre productividad en
proyectos Python de mediana complejidad (Pressman & Maxim, 2021). El
total de horas-hombre estimado constituirá la línea base contra la cual
se medirán los tiempos reales registrados por los agentes SDLC-AI
mediante los timestamps de los logs de Antigravity.

#### Factor de Conversión a Horas-Hombre ($E_{trad}$)

A partir de la descomposición funcional en Puntos de Historia ($PH_i$) y la velocidad de referencia de 10 $PH$ por semana-programador, se adopta una dedicación efectiva de 30 horas-hombre por semana-programador (Pressman & Maxim, 2021). Esto define una constante paramétrica de conversión de:

$$r = \frac{30\text{ horas-hombre}}{10\text{ }PH} = 3{,}0\text{ horas-hombre por cada } 1\text{ }PH$$

El esfuerzo tradicional total ($E_{trad}$), expresado en horas-hombre, se formaliza como:

$$E_{trad} = \sum_{i=1}^{n} PH_i \times 3{,}0\text{ h}$$

#### Desglose Paramétrico por Fase del SDLC

Para permitir la comparación cuantitativa del tiempo de desarrollo por fase establecido en la Sección 3.3, $E_{trad}$ se distribuye de acuerdo con las ponderaciones estándar de la ingeniería de software:

- **Fase A — Análisis y Especificación:** 20 % ($0{,}20 \times E_{trad}$)
- **Fase B — Diseño Técnico y Arquitectura:** 15 % ($0{,}15 \times E_{trad}$)
- **Fase C — Codificación y Desarrollo:** 35 % ($0{,}35 \times E_{trad}$)
- **Fase D — Pruebas y QA:** 20 % ($0{,}20 \times E_{trad}$)
- **Fase E — Despliegue y Empaquetado:** 10 % ($0{,}10 \times E_{trad}$)

#### Tiempo Real de SDLC-AI ($T_{SDLC-AI}$) y Criterio de Éxito de la Hipótesis

El tiempo total del framework propuesto ($T_{SDLC-AI}$) consolida el tiempo humano-agente cronometrado en la Etapa 1 (Fase A) más la sumatoria de los tiempos de ejecución y autocorrección autónoma registrados en los *timestamps* de los logs de Antigravity durante la Etapa 2 (Fases B, C, D y E):

$$T_{SDLC-AI} = T_{\text{asistido}}(\text{Fase A}) + \sum_{k \in \{B, C, D, E\}} T_{\text{autónomo}}(k)$$

La reducción porcentual del tiempo de desarrollo ($\Delta T$) se calcula mediante:

$$\Delta T (\%) = \left( \frac{E_{trad} - T_{SDLC-AI}}{E_{trad}} \right) \times 100$$

El criterio de éxito para comprobar la hipótesis de investigación exige alcanzar:

$$\Delta T (\%) \ge 30\%$$

manteniendo de forma simultánea los siguientes umbrales de calidad y desempeño:
- `pylint score` $\ge 7{,}0 / 10{,}0$ sobre los módulos generados.
- Cobertura de pruebas unitarias con `pytest-cov` $\ge 80\%$.
- Precisión analítica de alertas de inventario con `F1-score` $\ge 0{,}80$.

### 3.1.2 Modelo de Intervención Humana --- Especificación Front-Loaded

El framework SDLC-AI opera bajo un modelo de **especificación
front-loaded con alta autonomía de ejecución**, fundamentado en el
principio de que una especificación completa, rigurosa y libre de
ambigüedades al inicio del proyecto minimiza el retrabajo, reduce el
consumo de tokens en las fases de ejecución y mejora la calidad de los
artefactos generados (Wang et al., 2024).

El modelo define dos etapas diferenciadas:

**Etapa 1 --- Fase de Especificación Asistida (intervención humana
activa):** El investigador colabora directamente con el Agente Analista
y el Agente Auditor de Especificaciones para producir el Documento de
Requisitos (SRS). El Agente Auditor tiene como función exclusiva revisar
el SRS producido por el Agente Analista, identificar ambigüedades,
inconsistencias, requisitos incompletos o conflictos lógicos, y generar
un reporte de observaciones que el investigador y el Agente Analista
resuelven iterativamente. La Fase de Especificación concluye únicamente
cuando el Agente Auditor emite un dictamen de aprobación sin
observaciones pendientes. Este SRS auditado es la única entrada al
pipeline autónomo.

**Etapa 2 --- Pipeline de Ejecución Autónoma (sin intervención humana en
tiempo de ejecución):** A partir del SRS aprobado, los agentes de
diseño, desarrollo, pruebas y despliegue operan de forma encadenada sin
requerir intervención humana adicional. Los mecanismos de control de
calidad son enteramente agénticos: el Agente Tester coordina con el
Agente Desarrollador las correcciones hasta superar los umbrales de
calidad; el Agente DevOps ejecuta el despliegue y genera el reporte
comparativo final. El investigador re-interviene únicamente al final del
pipeline para realizar la **evaluación comparativa** de métricas contra
la línea base.

## 3.2 Actividades por Fase

### Fase A --- Especificación Asistida (Investigador + Agente Analista + Agente Auditor)

Esta fase es la única donde el investigador interviene activamente en el
proceso. Comprende:

- Sesión de elicitación de requisitos del caso de estudio, donde el
  investigador describe el dominio del problema al Agente Analista.

- El Agente Analista estructura los requisitos funcionales, no
  funcionales y las restricciones del sistema de alertas en formato SRS
  estándar, incluyendo KPIs de inventario (nivel de servicio, cobertura
  en días, tasa de quiebre de stock).

- El Agente Auditor de Especificaciones revisa el SRS, emite un reporte
  de observaciones categorizadas por severidad (crítica, mayor, menor) y
  propone resoluciones.

- El investigador y el Agente Analista resuelven las observaciones
  iterativamente hasta obtener la aprobación del Agente Auditor.

- **Artefacto de salida:** SRS v1.0 auditado y aprobado. Este documento
  es inmutable una vez aprobado; cualquier cambio posterior requeriría
  reiniciar esta fase.

### Fase B --- Diseño y Arquitectura Autónomos (Agente Arquitecto)

A partir del SRS aprobado, el Agente Arquitecto opera de forma autónoma:

- Diseña el pipeline de datos: fuentes (CSV/JSON de inventario
  simulado), transformaciones y carga.

- Define la arquitectura modular en Python aplicando principios SOLID.

- Diseña el esquema de orquestación inter-agente: protocolos de paso de
  mensajes y gestión de estado compartido.

- Genera diagramas de arquitectura y el Documento de Diseño Técnico
  (TDD).

- **Artefacto de salida:** TDD v1.0 con diagramas. El pipeline continúa
  automáticamente.

### Fase C --- Desarrollo Autónomo (Agente Desarrollador)

El Agente Desarrollador genera el código fuente a partir exclusivamente
del TDD:

- Implementa los módulos de ingesta y transformación de datos de
  inventario.

- Desarrolla el motor de alertas: lógica de cálculo de indicadores y
  umbralización configurable.

- Implementa la capa de integración con la API de Google Gemini Pro para
  generación de reportes narrativos.

- Genera documentación inline (docstrings) y README del proyecto.

- **Artefacto de salida:** código fuente Python completo.

### Fase D --- Pruebas y QA Autónomos (Agente Tester ↔ Agente Desarrollador)

El Agente Tester valida la solución y coordina correcciones sin
intervención humana:

- Genera conjuntos de datos de prueba que simulan escenarios de quiebre
  de stock, sobreabastecimiento y distribución ineficiente.

- Ejecuta pruebas unitarias e integradas sobre los módulos críticos.

- Mide cobertura de código (pytest-cov) y precisión de alertas
  (F1-score) contra los umbrales definidos en el SRS.

- En caso de fallo, coordina con el Agente Desarrollador las
  correcciones necesarias y re-ejecuta las pruebas hasta superar todos
  los umbrales.

- **Artefacto de salida:** reporte de QA con métricas finales.

### Fase E --- Despliegue y Evaluación Autónomos (Agente DevOps)

El Agente DevOps cierra el pipeline autónomo:

- Configura el entorno de ejecución y gestiona dependencias
  (requirements.txt, entornos virtuales).

- Genera el reporte final de evaluación del framework SDLC-AI con las
  métricas de tiempo, calidad y lecciones aprendidas.

- **Artefacto de salida:** sistema desplegado + reporte comparativo
  preliminar SDLC-AI vs. línea base.

**Evaluación Final (Investigador):** El investigador realiza la revisión
del reporte comparativo, valida las métricas y redacta las conclusiones
del trabajo de grado.

## 3.3 Métricas de Evaluación del Framework SDLC-AI

Con el propósito de evaluar rigurosamente los resultados del framework
SDLC-AI, se definen a continuación las métricas que guiarán la medición
del desempeño del proceso y del producto. Estas métricas responden a la
pregunta de investigación y permiten contrastar el enfoque agéntico con
el desarrollo tradicional:

| Métrica | Qué mide | Instrumento | Criterio de éxito |
|---|---|---|---|
| **Tiempo de desarrollo por fase** | Horas-hombre invertidas por cada agente en cada fase del SDLC | Timestamps en logs de ejecución de Antigravity | Reducción ≥ 30 % vs. estimado de desarrollo tradicional |
| **Calidad del código generado** | Análisis estático del código producido por el Agente Desarrollador | pylint score sobre el módulo generado | Puntaje ≥ 7,0 / 10,0 |
| **Cobertura de pruebas** | Porcentaje de cobertura de las pruebas unitarias generadas por el Agente Tester | pytest-cov sobre la suite de pruebas | Cobertura ≥ 80 % |
| **Precisión de alertas de inventario** | Tasa de acierto de las alertas generadas sobre el dataset de validación | F1-score calculado sobre dataset de prueba | F1-score ≥ 0,80 |
| **Trazabilidad del proceso** | Registro completo de decisiones y artefactos generados por fase | Revisión cualitativa de logs y documentos producidos | 100 % de las fases con artefacto documentado |

El registro de estas métricas se realizará de forma continua durante el
desarrollo del proyecto, constituyendo la base del reporte de evaluación
comparativa que se entregará como producto final del trabajo de grado.

# 4. CRONOGRAMA DE ACTIVIDADES

El proyecto se desarrolla en un periodo de dieciséis semanas (cuatro
meses), organizadas en un modelo iterativo e incremental con cuatro
Sprints de construcción del caso de estudio. Cada Sprint integra todas
las fases del pipeline SDLC-AI sobre un incremento funcional del
sistema. El periodo incluye cuatro hitos de entrega formales alineados
con el calendario académico del semestre 2026-02.

| Etapa / Sprint | Actividades y Artefactos Clave | Roles / Agentes | Semanas | Entregable / Hito |
|---|---|---|---|---|
| **INICIO — Diseño del Framework y Línea Base** | Diseño de la arquitectura de agentes SDLC-AI y estimación paramétrica de la línea base tradicional. | Investigador | S1–S2 | **Anteproyecto entregado** (Sem. 1) |
| **FASE A — Especificación Asistida** | Elicitación de requisitos (Investigador + Ag. Analista), auditoría formal de ambigüedades (Ag. Auditor) e iteraciones de refinamiento. Salida: SRS v1.0 inmutable. | Investigador, Agente Analista, Agente Auditor | S2–S3 | **SRS v1.0 auditado y aprobado** (Sem. 3) |
| **SPRINT 1 — Módulo de Ingesta de Datos** | Fase B (Arquitecto: diseño ETL y pipeline de datos).<br>Fase C (Desarrollador: `data_ingestion.py` y `kpi_calculator.py`).<br>Fase D (Tester: pruebas unitarias de ingesta y validación de esquema). | Agente Arquitecto, Agente Desarrollador, Agente Tester | S4–S5 | **ENTREGA 1: Prototipo Funcional** (Sem. 5, 29-sep) |
| **SPRINT 2 — Motor de Alertas + KPIs** | Fase B (Arquitecto: diseño del motor de alertas).<br>Fase C (Desarrollador: `alert_engine.py` y umbrales configurables).<br>Fase D (Tester: pruebas integrales de detección y evaluación de F1-score). | Agente Arquitecto, Agente Desarrollador, Agente Tester | S6–S8 | Incremento funcional validado |
| **SPRINT 3 — Integración Gemini Pro + Reportes** | Fase B (Arquitecto: diseño de la capa de integración con Gemini Pro).<br>Fase C (Desarrollador: `gemini_reporter.py` para generación narrativa).<br>Fase D (Tester: pruebas end-to-end de consistencia narrativa). | Agente Arquitecto, Agente Desarrollador, Agente Tester | S9–S10 | **ENTREGA 2: Sistema Completo y Probado** (Sem. 10, 3-nov) |
| **SPRINT 4 — Despliegue + Reporte Comparativo** | Fase E (DevOps: empaquetado, `requirements.txt`, `README` de despliegue) y generación del reporte comparativo cuantitativo SDLC-AI vs. línea base. | Agente DevOps, Investigador | S11–S13 | Sistema desplegado y reporte comparativo preliminar |
| **CIERRE — Documento Final y Sustentación** | Consolidación y evolución del documento a Formato ETIC 2026 (S14–S15) y preparación de la sustentación oral (S15–S16). | Investigador | S14–S16 | **ENTREGA FINAL y Sustentación** (Sem. 16, 15-dic) |

## 4.1 Entregables del Proyecto

| Entregable | Descripción | Fecha de Entrega | Puntos |
|---|---|---|---|
| **Anteproyecto** | Documento de planteamiento del problema, objetivos, justificación, revisión de literatura inicial y cronograma. | 8 de septiembre de 2026 (23:55) | 50 |
| **Entrega 1 — Prototipo Funcional** | Prototipo del sistema de alertas con arquitectura definida y al menos un módulo funcional de ingesta de datos. | 29 de septiembre de 2026 (23:55) | 75 |
| **Entrega 2 — Sistema Codificado y Probado** | Sistema de alertas completo, suite de pruebas ejecutada y reporte de QA generado por el Agente Tester. | 3 de noviembre de 2026 (23:55) | 125 |
| **Entrega Final y Sustentación** | Despliegue final, reporte de evaluación del framework SDLC-AI y sustentación oral del proyecto. | 15 de diciembre de 2026 (23:55) | 250 |

# 5. RESULTADOS ESPERADOS

## 5.1 Generación de Conocimiento y Desarrollo Tecnológico

El producto tecnológico central del proyecto es un framework funcional
SDLC-AI implementado en Python, que incluye los módulos de orquestación
de los cinco agentes especializados y el sistema de alertas tempranas de
inventario como caso de uso validado. Este framework será documentado y
publicado como repositorio académico, con potencial de servir como
referencia para proyectos similares en el campo de la IA aplicada al
desarrollo de software.

Adicionalmente, se espera generar un reporte de evaluación comparativa
que documente, con métricas concretas, la diferencia en tiempos de
desarrollo, calidad del código y cobertura funcional entre el enfoque
SDLC-AI y un enfoque de desarrollo tradicional para el mismo caso de
uso.

## 5.2 Fortalecimiento de la Capacidad Científica Nacional

Este trabajo de grado, al ser sustentado y aprobado en el programa de
Ingeniería de Software del Politécnico Grancolombiano, contribuye a la
formación de capital humano especializado en IA aplicada a la industria.
La documentación generada tiene el potencial de ser incorporada como
material de referencia en cursos de Ingeniería de Software y de
Inteligencia Artificial en instituciones de educación superior
colombianas.

## 5.3 Apropiación Social del Conocimiento

Los resultados del proyecto serán presentados en el proceso de
sustentación pública del trabajo de grado. Se explorará la posibilidad
de presentar los hallazgos como ponencia en un evento académico de
ingeniería de sistemas o inteligencia artificial en Colombia. El
repositorio de código y la documentación serán accesibles públicamente,
favoreciendo la transferencia de conocimiento a la comunidad de
desarrolladores de software colombiana interesada en la aplicación de IA
en sus procesos.

## 5.4 Impactos Esperados

- **Impacto Económico:** demostración de la viabilidad de reducir costos
  y tiempos de desarrollo de software analítico para el sector retail
  mediante IA agéntica, con potencial de adopción por parte de pequeñas
  y medianas empresas del sector.

- **Impacto Social:** contribución a la competitividad del sector retail
  de moda colombiano mediante herramientas analíticas más accesibles y
  de más rápido desarrollo.

- **Impacto Académico:** generación de evidencia empírica sobre las
  capacidades y limitaciones actuales de la IA agéntica en el contexto
  de la Ingeniería de Software, enriqueciendo el debate académico en
  esta disciplina en Colombia.

- **Impacto Tecnológico:** establecimiento de un modelo de referencia
  (SDLC-AI) replicable en otros contextos industriales y académicos
  donde la velocidad de desarrollo de software sea un factor crítico.

# REFERENCIAS

Chopra, S., & Meindl, P. (2022). *Supply chain management: Strategy,
planning, and operation* (7th ed.). Pearson Education.

Ferreira, K. J., Lee, B. H. A., & Simchi-Levi, D. (2016). Analytics for
an online retailer: Demand forecasting and price optimization.
*Manufacturing & Service Operations Management*, *18*(1), 69--88.
<https://doi.org/10.1287/msom.2015.0561>

Gemini Team, Google DeepMind. (2024). *Gemini 1.5: Unlocking multimodal
understanding across millions of tokens of context* (arXiv:2403.05530).
arXiv. <https://doi.org/10.48550/arXiv.2403.05530>

Hong, S., Zheng, X., Chen, J., Cheng, Y., Wang, J., Zhang, C., Wang, Z.,
Yau, S. K. S., Lin, Z., Zhou, L., Ran, C., Xiao, L., Wu, C., &
Schmidhuber, J. (2024). MetaGPT: Meta programming for a multi-agent
collaborative framework. In *The Twelfth International Conference on
Learning Representations (ICLR 2024)*.
<https://doi.org/10.48550/arXiv.2308.00352>

Inexmoda. (2024). *Informe del Observatorio Sistema Moda: Dinámica del
consumo de moda en Colombia*. Instituto para la Exportación y la Moda.
<https://inexmoda.org.co>

Kuhrmann, M., Tell, P., Hebig, R., Klünder, J., Münch, J., Linssen, O.,
Pfahl, D., Felderer, M., Prause, C. R., MacDonell, S. G.,
Nakatumba-Nabende, J., Raffo, D., Beecham, S., Tüzün, E., & López, G.
(2022). What makes agile software development agile? *IEEE Transactions
on Software Engineering*, *48*(9), 3523--3539.
<https://doi.org/10.1109/TSE.2021.3099532>

Pressman, R. S., & Maxim, B. R. (2021). *Software engineering: A
practitioner's approach* (9th ed.). McGraw-Hill Education.

Qian, C., Cong, X., Yang, C., Chen, W., Su, Y., Xu, J., Liu, Z., & Sun,
M. (2024). Communicative agents for software development. In
*Proceedings of the 62nd Annual Meeting of the Association for
Computational Linguistics (Volume 1: Long Papers)* (pp. 14897--14910).
Association for Computational Linguistics.
<https://doi.org/10.18653/v1/2024.acl-long.804>

Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., Chen, Z.,
Tang, J., Chen, X., Lin, Y., Zhao, W. X., Wei, Z., & Wen, J.-R. (2024).
A survey on large language model based autonomous agents. *Frontiers of
Computer Science*, *18*(6), 186345.
<https://doi.org/10.1007/s11704-024-40231-1>
