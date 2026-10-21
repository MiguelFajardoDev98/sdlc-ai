Miguel Ángel Fajardo Cossio
C.C. 1234990751
Asesor: Wilson Eduardo Soto Forero
Politécnico Grancolombiano — Facultad de Ingeniería, Diseño e Innovación

Octubre de 2026

# RESUMEN

El presente proyecto de grado de investigación aplicada diseña, implementa y evalúa el framework **SDLC-AI**, una arquitectura de orquestación de agentes autónomos de Inteligencia Artificial orientada a la automatización estructurada de las fases del Ciclo de Vida del Desarrollo de Software (SDLC): análisis de requisitos, diseño arquitectónico, desarrollo, pruebas y despliegue. Como caso de estudio y dominio de validación empírica, el framework se aplica a la construcción de un sistema analítico de alertas tempranas de inventario para el sector retail de moda en Colombia.

Frente a los enfoques tradicionales de asistencia por IA basados en chats conversacionales aislados, SDLC-AI establece una separación metodológica estricta en dos fases: una **Fase de Especificación Asistida**, donde el investigador colabora interactivamente con un Agente Analista y un Agente Auditor para producir un Documento de Requisitos (SRS) libre de ambigüedades; y un **Pipeline de Ejecución Autónoma**, donde los agentes Arquitecto, Desarrollador, Tester y DevOps operan de forma encadenada sin intervención humana. Este modelo de especificación *front-loaded* mitiga el retrabajo y previene la propagación de errores en etapas tardías. La evaluación experimental contrasta cuantitativamente los tiempos de desarrollo y la calidad del código (pylint score >= 7.0, pytest-cov >= 80% y F1-score >= 0.80) contra una línea base paramétrica tradicional (), comprobando la hipótesis de reducción de tiempo ().

**Palabras clave:** Inteligencia Artificial Agéntica, Ciclo de Vida del Software (SDLC), Orquestación Multi-Agente, Especificación Front-Loaded, Evaluación Comparativa, Google Gemini Pro, Antigravity, Retail de Moda.

# CAPÍTULO 1: INTRODUCCIÓN

## 1.1 Contextualización del Sector Retail de Moda en Colombia

El sector retail de moda en Colombia representa uno de los dinamizadores más significativos de la economía nacional, caracterizado por una alta intensificación del empleo, márgenes comerciales ajustados y una estructura operativa con marcada presencia de micro, pequeñas y medianas empresas (Ferreira et al., 2016; Inexmoda, 2024). En este entorno, la gestión logística y la distribución de inventarios constituyen un desafío crítico. Las cadenas de suministro de moda enfrentan una dinámica de consumo volátil, ciclos de vida de producto reducidos y una fragmentación multidimensional de las referencias por SKU (Stock Keeping Unit), combinando atributos de color, talla, categoría y temporalidad estacional.

La dispersión geográfica de los puntos de venta y los desbalances de inventario generan de manera recurrente dos problemas logísticos extremos: el quiebre de stock (*stockout*) en referencias de alta demanda —lo cual conlleva ventas perdidas y deterioro de la fidelidad del cliente—, y el sobrestock (*overstock*) en referencias de baja rotación, que satura la capacidad física de almacenamiento, inmoviliza capital de trabajo y fuerza rebajas comerciales destructivas (Chopra & Meindl, 2022).

Para responder a estos retos, las empresas requieren sistemas de información analíticos capaces de monitorear en tiempo real variables críticas como la cobertura de inventario en días, el nivel de servicio y la velocidad de rotación, emitiendo alertas tempranas para habilitar redistribuciones oportunas de mercancía.

## 1.2 Formulación del Problema en Ingeniería de Software

Desde la disciplina de la Ingeniería de Software, la construcción de soluciones analíticas personalizadas para resolver problemáticas del retail enfrenta una limitación de fondo: los ciclos de desarrollo tradicionales son lentos, intensivos en esfuerzo humano y costosos (Pressman & Maxim, 2021). El tiempo transcurrido entre el levantamiento de requisitos, el diseño de la arquitectura, la codificación manual, la elaboración de casos de prueba y el despliegue suele extenderse a lo largo de semanas o meses. Cuando el software analítico finalmente entra en operación, las condiciones comerciales y los patrones de demanda de la temporada textil ya han mutado (Kuhrmann et al., 2022).

La adopción de herramientas de Inteligencia Artificial Generativa ha introducido mejoras en la productividad individual de los desarrolladores; sin embargo, su uso aislado en interfaces de chat continúa demandando un humano en el medio (*human-in-the-loop*) permanente, fragmentando el flujo de trabajo y generando vacíos de trazabilidad. Surge, por ende, la oportunidad de modelar el ciclo de vida del software como un sistema coordinado de agentes inteligentes con roles especializados, capaces de razonar, planificar, invocar herramientas y comunicarse entre sí de manera estructurada (Wang et al., 2024).

A partir de esta doble problemática —operativa en el retail textil y metodológica en la producción de software—, se formula la pregunta de investigación rectora:

***¿En qué medida el framework de orquestación de agentes autónomos SDLC-AI reduce el tiempo de desarrollo y mantiene la calidad del código producido —medida por pylint score, cobertura de pruebas y precisión analítica— en comparación con la estimación de esfuerzo de un desarrollo tradicional equivalente, al construir un sistema de alertas de inventario para el sector retail de moda en Colombia?***

## 1.3 Justificación Técnico-Científica

La pertinencia del proyecto se articula en tres dimensiones: 1. **Dimensión Tecnológica:** Explora la frontera contemporánea de la Inteligencia Artificial Agéntica, aprovechando modelos fundacionales de última generación como Google Gemini Pro (Gemini Team et al., 2024), dotados de ventanas de contexto extendido y mecanismos nativos de llamada a herramientas (*Tool Calling*), articulados mediante el motor de orquestación Antigravity. 2. **Dimensión Disciplinar en Ingeniería de Software:** Contribuye a la literatura de ingeniería aumentada por IA, investigando empíricamente la efectividad de una arquitectura multi-agente inspirada en marcos como ChatDev (Qian et al., 2024) y MetaGPT (Hong et al., 2024), pero introduciendo la separación entre una fase de especificación asistida y un pipeline de ejecución autónoma para minimizar el consumo de recursos computacionales. 3. **Dimensión Sectorial y Económica:** Aporta un caso de uso práctico orientado a mitigar pérdidas económicas en el retail de moda colombiano, sentando las bases para que pequeñas y medianas organizaciones accedan a herramientas analíticas avanzadas sin incurrir en costos prohibitivos de consultoría técnica (Ferreira et al., 2016; Inexmoda, 2024).

## 1.4 Alcance y Limitaciones

1. **Alcance Incluido:**

  2. Diseño e implementación formal del framework SDLC-AI con cinco roles agénticos.

  3. Implementación del sistema de alertas tempranas de inventario con ingesta de datos, cálculo de KPIs (días de inventario, nivel de servicio), motor de reglas y reportería narrativa con Gemini Pro.

  4. Evaluación cuantitativa mediante calidad de código (pylint), cobertura (pytest-cov), precisión analítica (F1-score) y reducción de tiempo ().

5. **Limitaciones y Exclusiones:**

  6. El sistema no se conecta directamente a bases de datos de ERPs transaccionales propietarios en producción; opera sobre esquemas estructurados normalizados y datasets de validación.

  7. No se realiza entrenamiento o ajuste fino (*fine-tuning*) de modelos base; se utilizan las capacidades inferenciales de Gemini Pro mediante API.

# CAPÍTULO 2: OBJETIVOS

## 2.1 Objetivo General

Diseñar, implementar y evaluar el framework **SDLC-AI**, un sistema de orquestación de agentes de Inteligencia Artificial Agéntica que automatiza las fases del Ciclo de Vida del Desarrollo de Software (SDLC) —análisis, diseño, desarrollo, pruebas y despliegue—, midiendo mediante métricas cuantitativas su impacto en la reducción de tiempos de desarrollo y la calidad del código producido con respecto a una estimación de desarrollo tradicional equivalente, a través de la construcción de un sistema de alertas de inventario para el sector retail de moda en Colombia como caso de estudio.

## 2.2 Objetivos Específicos

1. **Diseñar la arquitectura del framework SDLC-AI**, definiendo los roles agénticos, el protocolo de orquestación entre agentes, los mecanismos de comunicación de estado y los puntos de intervención humana en la Fase de Especificación Asistida.

2. **Producir la especificación completa y auditada del caso de estudio**, mediante la colaboración del investigador con el Agente Analista y el Agente Auditor de Especificaciones, generando un Documento de Requisitos (SRS) libre de ambigüedades que sirva como entrada única al pipeline de ejecución autónoma.

3. **Ejecutar el pipeline de diseño y desarrollo de forma autónoma**, donde el Agente Arquitecto genera el diseño técnico (TDD) y el Agente Desarrollador produce el código fuente del sistema de alertas a partir exclusivamente de la especificación aprobada, sin intervención humana adicional.

4. **Validar la solución de forma autónoma**, mediante el Agente Tester que ejecuta pruebas unitarias e integradas, mide la cobertura de código y la precisión de alertas, y coordina con el Agente Desarrollador las correcciones necesarias hasta superar los umbrales de calidad definidos.

5. **Comparar cuantitativamente** los tiempos de desarrollo y métricas de calidad del pipeline SDLC-AI contra la línea base de estimación paramétrica tradicional, identificando el impacto del modelo de especificación front-loaded sobre la eficiencia del pipeline autónomo.

# CAPÍTULO 3: MARCO TEÓRICO Y REVISIÓN DE LITERATURA

## 3.1 Inteligencia Artificial Agéntica en la Ingeniería de Software

La Inteligencia Artificial Agéntica define una clase de sistemas basados en modelos de lenguaje grande (LLM) que trascienden el paradigma de respuesta textual pasiva para comportarse como entidades autónomas capaces de percibir su entorno, planificar cursos de acción, descomponer problemas complejos e interactuar con herramientas externas mediante ejecución de código y llamadas a APIs (Wang et al., 2024).

En el campo de la Ingeniería de Software, la evolución desde asistentes conversacionales de código hacia sistemas multi-agente colaborativos ha demostrado que la especialización funcional de agentes —donde cada instancia asume un rol profesional claramente diferenciado (analista, arquitecto, ingeniero de pruebas)— permite resolver tareas complejas de desarrollo con mayor consistencia. Investigaciones como ChatDev (Qian et al., 2024) y MetaGPT (Hong et al., 2024) evidencian que el establecimiento de Procedimientos Operativos Estándar (SOP) y contratos de artefactos intermedios reduce el ruido semántico y evita la degradación del contexto.

## 3.2 Ecosistema Google Gemini Pro y Antigravity

El framework SDLC-AI adopta como motor cognitivo el modelo **Google Gemini Pro** (Gemini Team et al., 2024). Este modelo multimodal ofrece ventajas arquitectónicas decisivas para la ingeniería agéntica: - **Ventana de Contexto Extendido:** Capacidad de procesar hasta un millón de tokens, permitiendo almacenar la especificación completa del sistema, trazas de ejecución y módulos de código completos sin truncamiento. - **Llamadas a Funciones Nativas (Tool Calling):** Protocolo estructurado para invocar herramientas locales de manipulación de archivos y ejecución de pruebas con baja tasa de error sintáctico. - **Razonamiento Estructurado:** Generación consistente de estructuras de datos (JSON, dataclasses) requeridas para la comunicación inter-agente.

La plataforma **Antigravity** actúa como el sustrato de ejecución y orquestación local, suministrando el arnés operativo (*harness*), el acceso seguro al sistema de archivos, la invocación de comandos de terminal y el registro sistemático de eventos de telemetría y métricas temporales.

## 3.3 Ciclo de Vida del Desarrollo de Software (SDLC) y Calidad Estática

El Ciclo de Vida del Desarrollo de Software proporciona el marco metódico para la concepción, construcción, aseguramiento de la calidad y puesta en producción de sistemas computacionales (Pressman & Maxim, 2021). En este proyecto se formalizan las fases clásicas del SDLC adaptadas al paradigma agéntico: - **Análisis de Requisitos:** Elicitación y especificación formal. - **Diseño Técnico:** Definición de arquitectura modular y esquemas de datos. - **Codificación:** Implementación de componentes limpios en Python. - **Pruebas y QA:** Verificación automatizada mediante suites unitarias e integradas (pytest), cobertura de líneas (pytest-cov) y análisis estático de adherencia a estándares (pylint). - **Despliegue:** Empaquetado portable de dependencias y scripts de ejecución.

## 3.4 Analítica de Datos y Gestión de Inventarios en Retail de Moda

El dominio de validación del framework es la analítica de inventarios en el sector moda en Colombia (Ferreira et al., 2016; Inexmoda, 2024). La literatura logística clásica (Chopra & Meindl, 2022) destaca tres indicadores esenciales para prevenir quiebres de stock y sobreabastecimiento: 1. **Días de Cobertura de Inventario (****):**

2. **Tasa de Quiebre de Stock (****):** Porcentaje de referencias activas con inventario en cero respecto al catálogo total. 3. **Nivel de Servicio (****):** Proporción de demanda satisfecha inmediatamente desde el stock disponible.

# CAPÍTULO 4: METODOLOGÍA Y ESTRATEGIA DE DESARROLLO

## 4.1 Enfoque de Investigación Aplicada e Iterativa

El proyecto adopta un enfoque de **investigación aplicada con diseño iterativo e incremental**. No persigue la formulación de teorías abstractas desconectadas de la práctica, sino la construcción y validación empírica de un artefacto tecnológico (el framework SDLC-AI) sobre un caso de estudio empresarial concreto. El desarrollo se estructura en cuatro Sprints de dos a tres semanas de duración, donde cada Sprint implementa y valida un incremento funcional de software.

## 4.2 Formalización Matemática de la Línea Base Paramétrica

Para contrastar rigurosamente el rendimiento del framework frente a la práctica convencional de ingeniería, se formaliza la línea base de desarrollo tradicional () utilizando el modelo paramétrico de Puntos de Historia () con escala Fibonacci () y velocidad estandarizada (Pressman & Maxim, 2021):

1. **Velocidad de productividad estándar:** .

2. **Jornada de dedicación efectiva:** .

3. **Factor paramétrico de conversión (****):**

El esfuerzo total estimado de la línea base tradicional se formaliza como:

### Distribución Paramétrica por Fase del SDLC

De acuerdo con las métricas históricas consagradas en la disciplina de software,  se desglosa proporcionalmente: - **Fase A (Análisis y Especificación):**  - **Fase B (Diseño Arquitectónico):**  - **Fase C (Codificación):**  - **Fase D (Pruebas y QA):**  - **Fase E (Despliegue y Empaquetado):** 

## 4.3 Modelo Front-Loaded: Fase Asistida vs. Pipeline Autónomo

La arquitectura metodológica de SDLC-AI opera bajo el principio de **especificación front-loaded**, minimizando el desperdicio computacional al garantizar que la especificación de requisitos no contenga ambigüedades antes de iniciar la construcción:

flowchart TD
 subgraph ETAPA_1 ["ETAPA 1: Fase de Especificación Asistida"]
 INV["Investigador Líder"] <--> ANA["Agente Analista"]
 ANA --> DRAFT["Borrador SRS (spec_draft.md)"]
 DRAFT <--> AUD["Agente Auditor"]
 AUD -->|Aprobación Formal| SRS_FINAL["SRS Aprobado (spec.md v1.0 Inmutable)"]
 end

 subgraph ETAPA_2 ["ETAPA 2: Pipeline de Ejecución Autónoma"]
 SRS_FINAL --> ARQ["Agente Arquitecto (TDD en plan.md)"]
 ARQ --> DEV["Agente Desarrollador (src/*.py)"]
 DEV <--> TEST["Agente Tester (tests/*.py)"]
 TEST -->|Quality Gate Aprobado| OPS["Agente DevOps (Empaquetado)"]
 end

### Medición de Tiempo Real y Validación de Hipótesis

El tiempo real de desarrollo consumido por el framework () se registra a través de las marcas de tiempo (*timestamps*) de Antigravity:

La reducción porcentual de tiempo de desarrollo () corresponde a:

**Criterio de Validación de la Hipótesis:** La hipótesis de investigación se considera formalmente demostrada si se cumple la condición:

garantizando simultáneamente los umbrales mínimos de calidad y desempeño: - pylint score  sobre los módulos en src/. - Cobertura de pruebas unitarias pytest-cov . - Precisión analítica de alertas de inventario F1-score .

## 4.4 Plan de Sprints y Cronograma General

| Etapa / Sprint | Actividades Clave | Roles Agénticos / Humanos | Semanas | Entregables / Hito |
| --- | --- | --- | --- | --- |
| INICIO: Harness y Línea Base | Configuración del arnés en Antigravity, definición de docs/constitution.md y estimación paramétrica . | Investigador | S1–S2 | Anteproyecto Aprobado (Semana 1) |
| FASE A: Especificación Asistida | Elicitación de requisitos, auditoría formal de ambigüedades y emisión de SRS v1.0. | Investigador, Agente Analista, Agente Auditor | S2–S3 | SRS v1.0 Aprobado (Semana 3) |
| SPRINT 1: Ingesta y KPIs | Arquitectura ETL, desarrollo de data_ingestion.py y kpi_calculator.py, pruebas unitarias con cobertura . | Agente Arquitecto, Agente Desarrollador, Agente Tester | S4–S5 | ENTREGA 1: Prototipo Funcional (2026-10-24) |
| SPRINT 2: Motor de Alertas | Diseño técnico, desarrollo de alert_engine.py y evaluación de precisión F1-score en detección de quiebres. | Agente Arquitecto, Agente Desarrollador, Agente Tester | S6–S8 | Incremento Funcional de Alertas |
| SPRINT 3: Integración Gemini Pro | Capa de reportes narrativos con Gemini Pro (gemini_reporter.py) y suite end-to-end. | Agente Arquitecto, Agente Desarrollador, Agente Tester | S9–S10 | ENTREGA 2: Sistema Completo y Probado (2026-11-16) |
| SPRINT 4: DevOps y Despliegue | Empaquetado portable, congelamiento de dependencias (requirements.txt), cálculo de . | Agente DevOps, Investigador | S11–S13 | Sistema Desplegado y Reporte Comparativo |
| CIERRE: Documento Final | Consolidación del informe final de grado en formato ETIC y sustentación oral. | Investigador | S14–S16 | ENTREGA FINAL y Sustentación (2026-12-13) |

# REFERENCIAS

Chopra, S., & Meindl, P. (2022). *Supply chain management: Strategy, planning, and operation* (7th ed.). Pearson Education.

Ferreira, K. J., Lee, B. H. A., & Simchi-Levi, D. (2016). Analytics for an online retailer: Demand forecasting and price optimization. *Manufacturing & Service Operations Management*, *18*(1), 69–88. 

Gemini Team, Google DeepMind. (2024). *Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context* (arXiv:2403.05530). arXiv. 

Hong, S., Zheng, X., Chen, J., Cheng, Y., Wang, J., Zhang, C., Wang, Z., Yau, S. K. S., Lin, Z., Zhou, L., Ran, C., Xiao, L., Wu, C., & Schmidhuber, J. (2024). MetaGPT: Meta programming for a multi-agent collaborative framework. In *The Twelfth International Conference on Learning Representations (ICLR 2024)*. 

Inexmoda. (2024). *Informe del Observatorio Sistema Moda: Dinámica del consumo de moda en Colombia*. Instituto para la Exportación y la Moda. 

Kuhrmann, M., Tell, P., Hebig, R., Klünder, J., Münch, J., Linssen, O., Pfahl, D., Felderer, M., Prause, C. R., MacDonell, S. G., Nakatumba-Nabende, J., Raffo, D., Beecham, S., Tüzün, E., & López, G. (2022). What makes agile software development agile? *IEEE Transactions on Software Engineering*, *48*(9), 3523–3539. 

Pressman, R. S., & Maxim, B. R. (2021). *Software engineering: A practitioner’s approach* (9th ed.). McGraw-Hill Education.

Qian, C., Cong, X., Yang, C., Chen, W., Su, Y., Xu, J., Liu, Z., & Sun, M. (2024). Communicative agents for software development. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 14897–14910). Association for Computational Linguistics. 

Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., Chen, Z., Tang, J., Chen, X., Lin, Y., Zhao, W. X., Wei, Z., & Wen, J.-R. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science*, *18*(6), 186345. 

# ANEXOS

## Anexo A: Estructura del Harness de Orquestación en Antigravity

El framework SDLC-AI opera mediante una estructura de archivos estandarizada que garantiza la gobernanza, persistencia y reproducibilidad de las ejecuciones agénticas: - docs/constitution.md: Principios inmutables de ingeniería y reglas metodológicas. - AGENTS.md: Especificación de roles, prompts de sistema y contratos de transición. - MEMORY.md: Estado vivo, cronograma de entregas y registro de decisiones arquitectónicas (ADRs). - specs/: Repositorio de especificaciones de requisitos (SRS) y diseños técnicos (TDD). - src/: Código fuente modular en Python. - tests/: Suites de pruebas automatizadas y fixtures de datos. - logs/: Trazabilidad empírica, métricas de ejecución y reportes de calidad en formato JSON.

## Anexo B: Matriz Preliminar de Requisitos del Sprint 1 (Ingesta y KPIs)

1. **HU-01: Ingesta y Validación de Inventario:** Capacidad de leer fuentes tabulares (CSV/JSON), sanitizar datos, validar tipos y descartar registros inconsistentes.

2. **HU-02: Cálculo de Días de Cobertura (****):** Computar la cobertura por referencia y punto de venta a partir del inventario disponible y la velocidad de venta histórica.

3. **HU-03: Detección Preliminar de Quiebre de Stock:** Identificar referencias con inventario igual a cero o cobertura inferior al umbral de seguridad configurado.
