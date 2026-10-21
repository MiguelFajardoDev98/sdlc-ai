# Flujo de trabajo del proyecto en GitHub

Guía para guardar, clonar y mantener SDLC-AI desde este equipo o desde
cualquier otro computador. El repositorio no debe publicar claves, archivos
`.env`, cachés ni credenciales.

## 1. Primera publicación en GitHub

Esta carpeta actualmente no tenía un repositorio Git local. Crea primero un
repositorio vacío en GitHub, sin README ni `.gitignore`, y conserva su URL.

Desde la raíz del proyecto:

```bash
cd /home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI
git init
git branch -M main
git add .
git status --short
git commit -m "chore: publish SDLC-AI framework"
git remote add origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main
```

Si GitHub solicita autenticación, utiliza GitHub CLI (`gh auth login`) o un
Personal Access Token; nunca pegues un token en archivos del proyecto ni en la
URL guardada en documentación.

Antes del primer `git add`, revisa:

```bash
git status --short
git check-ignore -v .env .coverage src/__pycache__
```

No publiques claves Gemini, archivos `.env`, artefactos temporales, caches ni
datos reales de clientes. El dataset actual es sintético.

## 2. Abrir el proyecto en otro equipo

```bash
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
chmod +x run.sh docx_to_markdown/run.sh
./run.sh
```

Para validar también el convertidor DOCX:

```bash
cd docx_to_markdown
./run.sh
cd ..
```

En Windows puede usarse WSL o Git Bash. La ruta absoluta del proyecto no debe
quedar hardcodeada en scripts ni documentación operativa.

## 3. Configuración local opcional

Solo si se desea utilizar Gemini:

```bash
cp .env.example .env
# Editar .env localmente; no hacer git add .env
```

Sin `GEMINI_API_KEY`, el pipeline principal usa el fallback determinista.

## 4. Flujo diario para modificar el repositorio

Siempre parte de `main` actualizado:

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/<descripcion-corta>
```

Para cambios de comportamiento, usa primero Antigravity en modo plan:

```text
/feature <solicitud concreta>
```

El flujo esperado es:

1. Coordinator clasifica la solicitud y activa skills mínimas.
2. Analyst crea `spec_draft.md`.
3. Auditor crea `audit_report.md`.
4. El sistema se detiene en `WAITING_APPROVAL`.
5. El investigador revisa y ejecuta `/approve-spec <task_id>`.
6. Architect genera `plan.md`.
7. Developer modifica código y pruebas.
8. Tester ejecuta quality gates y corrige mediante el loop QA.
9. DevOps actualiza empaquetado y métricas.

No se debe modificar un `spec.md` aprobado directamente.

## 5. Validación antes de publicar cambios

Para el framework principal:

```bash
./run.sh
python3 scripts/validate_agent_harness.py
PYTHONPATH=. pytest tests/test_agent_harness.py -q
```

Para el subproyecto DOCX:

```bash
cd docx_to_markdown
./run.sh
cd ..
```

Revisa después:

```bash
git diff --check
git status --short
git diff --stat
```

Acepta un cambio solo si las pruebas relevantes pasan y la documentación
describe las métricas generadas por la última ejecución.

## 6. Commit, publicación y Pull Request

```bash
git add <archivos-intencionados>
git diff --cached --check
git commit -m "feat: <descripcion breve>"
git push -u origin feat/<descripcion-corta>
```

En GitHub abre un Pull Request hacia `main` con:

- objetivo del cambio;
- artefactos modificados;
- skills y agentes involucrados;
- comandos ejecutados y resultados;
- riesgos o decisiones pendientes.

No uses `git add .` sin revisar antes el estado, especialmente si hay archivos
generados por conversiones o logs locales.

## 7. Sincronizar otro equipo después de un Pull Request

```bash
git switch main
git pull --ff-only origin main
git branch --merged
```

Para continuar una rama existente:

```bash
git fetch origin
git switch feat/<descripcion-corta>
git pull --ff-only
```

## 8. Convenciones mínimas

- Ramas: `feat/`, `fix/`, `docs/`, `test/`, `chore/`.
- Commits: verbo breve y alcance claro.
- Cambios de requirements: ejecutar instalación y validación completa.
- Cambios de agentes/skills: ejecutar `scripts/validate_agent_harness.py`.
- Cambios en `src/`: ejecutar `./run.sh`.
- Cambios en `docx_to_markdown/`: ejecutar su `run.sh`.
- Nunca incluir secretos ni modificar historial remoto destructivamente.

