# ============================================
# Prompts especializados para análisis de código
# ============================================

# app/prompts/templates/code_analysis.py

from app.prompts.base import PromptTemplate

CODE_QUALITY_ANALYSIS = PromptTemplate(
    name="code_quality_analysis",
    system_message="Eres un experto senior en revisión de código y arquitectura de software.",
    template="""Analiza la calidad del código basándote en el siguiente contexto.

**Repositorio:** {repo_name}

**Contexto del código:**
{code_context}

**Áreas de enfoque:** {focus_areas}

**Genera un análisis detallado que incluya:**

1. **Puntuación General** (0-10)
   - Legibilidad
   - Mantenibilidad
   - Escalabilidad
   - Seguridad

2. **Patrones de Diseño**
   - Patrones identificados (buenos)
   - Anti-patrones encontrados

3. **Organización del Código**
   - Estructura de directorios
   - Separación de responsabilidades
   - Modularidad

4. **Buenas Prácticas**
   - ✅ Qué se hace bien
   - ❌ Qué se hace mal
   - 💡 Oportunidades de mejora

5. **Deuda Técnica**
   - Áreas que necesitan refactoring
   - Código duplicado
   - Complejidad excesiva

6. **Recomendaciones Priorizadas**
   - P0 (Crítico)
   - P1 (Importante)
   - P2 (Deseable)

Formato: Markdown estructurado con emojis para claridad.""",
    variables=["repo_name", "code_context", "focus_areas"],
    temperature=0.7,
    max_tokens=2000
)

IMPROVEMENT_PLAN = PromptTemplate(
    name="improvement_plan",
    system_message="Eres un arquitecto de software que crea planes de mejora accionables.",
    template="""Genera un plan de mejora detallado para el repositorio.

**Repositorio:** {repo_name}
**Tipo de mejora:** {improvement_type}

**Contexto relevante:**
{code_context}

**Genera un plan estructurado:**

## 📋 Plan de Mejora: {improvement_type}

### 1️⃣ Mejoras Identificadas

Para cada mejora, usa este formato:

#### Mejora #N: [Título descriptivo]
- **Problema actual:** Descripción clara del issue
- **Impacto:** 🔴 Alto / 🟡 Medio / 🟢 Bajo
- **Prioridad:** P0 (crítico) / P1 (importante) / P2 (deseable) / P3 (nice-to-have)
- **Esfuerzo estimado:** 1-5 días
- **Archivos afectados:**
  ```
  - path/to/file1.py
  - path/to/file2.py
  ```
- **Solución propuesta:**
  Descripción técnica de cómo implementar

- **Código de ejemplo:**
  ```python
  # Antes
  ...
  
  # Después
  ...
  ```

### 2️⃣ Dependencias entre Mejoras

```mermaid
graph TD
    A[Mejora #1] --> B[Mejora #2]
    B --> C[Mejora #3]
```

### 3️⃣ Timeline Sugerido

| Semana | Mejoras | Prioridad |
|--------|---------|-----------|
| 1      | #1, #2  | P0        |
| 2      | #3, #4  | P1        |
| 3      | #5, #6  | P2        |

### 4️⃣ Checklist de Implementación

- [ ] Mejora #1: [Título]
  - [ ] Modificar archivo X
  - [ ] Actualizar tests
  - [ ] Documentar cambios
- [ ] Mejora #2: [Título]
  ...

### 5️⃣ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| ...    | Alta/Media/Baja | Alto/Medio/Bajo | ... |

Sé específico, técnico y accionable.""",
    variables=["repo_name", "improvement_type", "code_context"],
    temperature=0.7,
    max_tokens=3000
)

BUG_DETECTION = PromptTemplate(
    name="bug_detection",
    system_message="Eres un experto en seguridad y detección de bugs en código.",
    template="""Analiza el código en busca de bugs y vulnerabilidades.

**Repositorio:** {repo_name}
**Categorías de bugs:** {bug_categories}

**Código a analizar:**
{code_context}

**Genera reporte de bugs:**

## 🐛 Reporte de Bugs y Vulnerabilidades

### Resumen Ejecutivo
- Total de issues: X
- Críticos: X | Altos: X | Medios: X | Bajos: X

### Issues Encontrados

#### 🔴 CRÍTICO: [Título del bug]
- **Archivo:** `path/to/file.py:línea`
- **Categoría:** SQL Injection / XSS / etc.
- **Descripción:** 
  Explicación del problema
  
- **Código problemático:**
  ```python
  # Línea problemática
  cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # ❌ SQL Injection
  ```

- **Impacto:** 
  Qué puede pasar si se explota

- **Solución:**
  ```python
  # Código corregido
  cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))  # ✅ Parametrizado
  ```

- **Referencias:**
  - OWASP: [link]
  - CWE: [link]

#### 🟡 MEDIO: [Otro bug]
...

### Recomendaciones Generales

1. **Inmediatas (< 1 día)**
   - Fix bugs críticos

2. **Corto plazo (< 1 semana)**
   - Fix bugs altos

3. **Mediano plazo (< 1 mes)**
   - Fix bugs medios

### Prevención

- Herramientas sugeridas: Bandit, Semgrep, etc.
- Linters a configurar
- Pre-commit hooks

Sé exhaustivo pero conciso.""",
    variables=["repo_name", "bug_categories", "code_context"],
    temperature=0.6,
    max_tokens=2500
)

MIGRATION_PLAN = PromptTemplate(
    name="migration_plan",
    system_message="Eres un experto en migraciones tecnológicas y modernización de código.",
    template="""Genera un plan detallado de migración.

**Repositorio:** {repo_name}
**Migración:** {migration_path}

**Análisis del código actual:**
{code_context}

**Genera plan de migración:**

## 🚀 Plan de Migración: {migration_path}

📊 Análisis Inicial
Estado Actual:

Tecnología: [actual]
Versiones: [lista]
Dependencias críticas: [lista]

Estado Objetivo:

Tecnología: [objetivo]
Versiones: [lista]
Nuevas dependencias: [lista]

🗺️ Fases de Migración
Fase 1: Preparación (Semana 1)

Auditoría completa

 Inventariar dependencias
 Identificar APIs deprecadas
 Listar breaking changes


Setup de entorno

 Crear branch de migración
 Configurar CI/CD para ambas versiones
 Preparar tests de regresión



Archivos a revisar:
- requirements.txt / package.json
- .github/workflows/
- docker-compose.yml
Fase 2: Migración Core (Semanas 2-3)
Prioridad 1: Archivos Críticos
ArchivoCambios NecesariosComplejidadTiempoapp/main.pyActualizar imports, sintaxisMedia2happ/models/Cambiar ORMAlta1 día
Cambios Comunes:
python# Antes (Python 2)
print "Hello"
dict.iteritems()

# Después (Python 3)
print("Hello")
dict.items()
Fase 3: Tests y Validación (Semana 4)

 Actualizar suite de tests
 Tests de integración
 Performance testing
 Security scanning

Fase 4: Deployment (Semana 5)

Staging

Deploy a staging
Smoke tests
Load testing


Production

Blue-green deployment
Rollback plan
Monitoring intensivo



📁 Archivos Afectados por Categoría
Config (Alta prioridad):

requirements.txt / package.json
Dockerfile
docker-compose.yml
.env.example

Core Logic (Media-Alta prioridad):

app/main.py
app/services/*.py
app/models/*.py

Tests:

tests/**/*.py

Docs:

README.md
CONTRIBUTING.md

⚠️ Breaking Changes Críticos

API Changes

old_function() → new_function()
Impacto: Todo el código


Sintaxis

Lista de cambios de sintaxis


Dependencias

old_package==1.0 → new_package==2.0



🔍 Checklist de Testing

 Unit tests pass (100%)
 Integration tests pass
 E2E tests pass
 Performance no degraded
 Security scan clean
 Code review completed

📈 Métricas de Éxito
MétricaBaselineTargetTest coverage75%80%Build time5 min4 minPerformance100ms≤ 100ms
🆘 Rollback Plan
Si algo falla:

Revertir deployment
Restaurar DB snapshot (si aplica)
Notificar equipo
Post-mortem

📚 Recursos

Guía oficial de migración: [link]
Breaking changes: [link]
Community forum: [link]

""",
    variables=["repo_name", "migration_path", "code_context"],
    temperature=0.7,
    max_tokens=3000
)