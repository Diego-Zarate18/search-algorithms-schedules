# Documento de Decisiones Técnicas e Implementación

**Proyecto:** Generación de horarios académicos sin conflictos mediante DFS + Backtracking  
**Materia:** Fundamentos de Inteligencia Artificial  
**Autores:** Ruiz Pérez Brian Luis & Zárate Vázquez Diego Alberto  

---

## 1. Arquitectura Técnica y Lenguaje
- **Lenguaje:** Python 3.10+
- **Paradigma:** Orientado a Objetos (POO), estructurado modularmente para facilitar la inspección del árbol de búsqueda.
- **Librerías:**
  - `matplotlib`: gráficas de métricas (retrocesos por nivel del árbol).
  - `pandas` (opcional): representación y exportación del horario final como tabla (días × bloques).

---

## 2. Dominio de Datos

### 2.1 Grupo y aula
- **Grupo objetivo:** 7° "A", Ingeniería en Tecnologías de la Información e Innovación Digital.
- **Aula:** `Aula 7A` (única y fija). El validador comprueba su disponibilidad, aunque en este escenario nunca está ocupada por otro grupo.

### 2.2 Materias, docentes y sesiones
La carga semanal suma 35 h, que multiplicadas por 15 semanas dan las 525 h del cuatrimestre.

| ID | Materia | Docente | Horas/semana | Sesiones |
|---|---|---|---|---|
| M1 | Fundamentos de Inteligencia Artificial | D1 | 6 | 3 × 2 h |
| M2 | Bases de Datos en la Nube (Optativa I) | D2 | 6 | 3 × 2 h |
| M3 | Seguridad Informática | D3 | 6 | 3 × 2 h |
| M4 | Inglés VI | D4 | 5 | 2 × 2 h + 1 × 1 h |
| M5 | Habilidades Gerenciales | D5 | 4 | 2 × 2 h |
| M6 | Formulación de Proyectos de Tecnología | D6 | 4 | 2 × 2 h |
| M7 | Ética y Legislación en Tecnologías de la Información | D7 | 4 | 2 × 2 h |
| | **Total** | | **35** | **18 sesiones** |

- Cada sesión se identifica como `Mx.k` (por ejemplo, `M1.2` es la sesión 2 de IA).
- La sesión `M4.3` dura 1 h: ocupa un bloque completo y la segunda hora queda libre para el grupo.
- Cada materia tiene un docente distinto, por lo que dentro de 7° "A" no hay conflictos de docente; solo importan sus ocupaciones con otros grupos.

### 2.3 Bloques horarios
- **Días:** Lunes a Viernes (`Lu`, `Ma`, `Mi`, `Ju`, `Vi`).
- **Bloques por día:** `B1` 08:00–10:00, `B2` 10:00–12:00, `B3` 12:00–14:00, `B4` 14:00–16:00.
- **Total:** 5 × 4 = 20 bloques semanales. Se usan 18 y quedan 5 horas libres (dos bloques completos y la hora sobrante de `M4.3`).

### 2.4 Exclusiones (documentadas en el planteamiento)
- Grupos 1°, 4°, 7° "B" y 7° "C": no se programan; solo aportan bloques ocupados de los docentes.
- Estadías (6° y 10°): sin clases presenciales, fuera del modelo.
- Tutoría grupal: no forma parte de la carga curricular, fuera del modelo.
- Laboratorio y otras aulas: fuera del modelo; todas las sesiones son en `Aula 7A`.

### 2.5 Matriz de ocupaciones previas de docentes
Bloques en los que cada docente ya imparte clase a otros grupos y, por lo tanto, no está disponible para 7° "A". Es un escenario ficticio pero verosímil, calibrado con un prototipo para que **tenga solución** y **obligue a retroceder**.

| Docente | Bloques ocupados |
|---|---|
| D1 (IA) | Lu-B1, Mi-B3, Ju-B3, Vi-B1, Vi-B4 |
| D2 (BD Nube) | Lu-B4, Mi-B2, Vi-B1, Vi-B2, Vi-B4 |
| D3 (Seguridad) | Lu-B2, Lu-B3, Mi-B1, Ju-B3, Ju-B4 |
| D4 (Inglés) | Lu-B4, Mi-B1, Ju-B2, Ju-B3 |
| D5 (Hab. Gerenciales) | Ma-B4, Mi-B1, Ju-B3, Vi-B3 |
| D6 (Formulación) | Mi-B1, Mi-B4, Ju-B1, Vi-B2 |
| D7 (Ética) | Lu-B4, Ju-B2, Ju-B3, Ju-B4 |

Vista por bloque (docentes ocupados):

| | Lu | Ma | Mi | Ju | Vi |
|---|---|---|---|---|---|
| **B1** 8–10 | D1 | | D3, D4, D5, D6 | D6 | D1, D2 |
| **B2** 10–12 | D3 | | D2 | D4, D7 | D2, D6 |
| **B3** 12–14 | D3 | | D1 | D1, D3, D4, D5, D7 | D5 |
| **B4** 14–16 | D2, D4, D7 | D5 | D6 | D3, D7 | D1, D2 |

---

## 3. Modelo de Búsqueda

### 3.1 Estado
Conjunto de asignaciones `(sesión, bloque, aula)`, donde `bloque = (día, B1..B4)`. Va de 0 a 18 asignaciones.

### 3.2 Restricciones (validación de cada candidato)
1. **Grupo:** el bloque no está ocupado por otra sesión de 7° "A".
2. **Docente:** el docente de la materia no tiene ese bloque en la matriz de ocupaciones.
3. **Distribución:** la materia no tiene otra sesión ese mismo día.
4. **Orden de sesiones:** para sesiones equivalentes de una materia (todas las de 2 h), la sesión `k` va en un día estrictamente posterior a la sesión `k-1`. En Inglés aplica solo entre `M4.1` y `M4.2`; `M4.3` (1 h) puede ir en cualquier día libre para Inglés.
5. **Aula:** `Aula 7A` libre en ese bloque (siempre se cumple en este escenario; se mantiene por generalidad).

### 3.3 Orden fijo de búsqueda (búsqueda no informada)
- **Sesiones:** `M1.1, M1.2, M1.3, M2.1, …, M7.2` (orden de la tabla 2.2).
- **Valores:** días de `Lu` a `Vi` y, dentro de cada día, bloques de `B1` a `B4`.
- No se reordenan sesiones ni valores durante la búsqueda (sin MRV, LCV ni forward checking).

### 3.4 Definición de métricas
| Métrica | Definición operativa |
|---|---|
| Validez | El horario final cumple las 5 restricciones (verificación independiente al terminar). |
| Materias asignadas | Materias con todas sus sesiones colocadas (objetivo 7; 18 sesiones). |
| Conflictos finales | Violaciones detectadas por la verificación final (objetivo 0). |
| Estados explorados | Cada candidato `(sesión, bloque)` evaluado por el validador, sea válido o no. |
| Retrocesos | Cada asignación válida que se deshace porque su rama no llevó a solución. Se registra el **nivel** (índice de la sesión, 0–17) donde ocurre. |
| Tiempo de resolución | Tiempo de cómputo de la búsqueda (`time.perf_counter`). |

### 3.5 Pseudocódigo

```python
def dfs_backtracking(k):                    # k = índice de la sesión actual (nivel del árbol)
    if k == len(sesiones):
        return True                         # Estado objetivo: 18 sesiones asignadas

    sesion = sesiones[k]
    for dia in DIAS:                        # Lu → Vi
        for bloque in BLOQUES:              # B1 → B4
            metricas.estados_explorados += 1
            if validador.es_valida(sesion, dia, bloque, estado):
                estado.agregar(sesion, dia, bloque, AULA)      # Actuador: asignar
                if dfs_backtracking(k + 1):
                    return True
                estado.remover(sesion)                         # Actuador: deshacer
                metricas.retrocesos += 1
                metricas.retrocesos_por_nivel[k] += 1
    return False                            # Ninguna opción válida: la rama falla
```

### 3.6 Resultado de referencia del prototipo
Con los datos de esta sección, un prototipo de validación obtuvo:
- Solución encontrada: **sí** (18/18 sesiones, 0 conflictos).
- Estados explorados: **1 834**.
- Retrocesos: **83**, concentrados en los niveles 12 a 16: 1, 3, 16, 21 y 42, en las sesiones de Inglés, Habilidades Gerenciales y Formulación de Proyectos.

| | Lu | Ma | Mi | Ju | Vi |
|---|---|---|---|---|---|
| **B1** 8–10 | M2.1 | M1.2 | M1.3 | M7.1 | M5.2 |
| **B2** 10–12 | M1.1 | M2.2 | M3.3 | M5.1 | M7.2 |
| **B3** 12–14 | M4.1 | M3.2 | M2.3 | M6.1 | M6.2 |
| **B4** 14–16 | M3.1 | M4.2 | M4.3 (1 h) | libre | libre |

La implementación final debe reproducir exactamente estos valores, porque la búsqueda es determinista. Esto sirve como prueba de correctitud.

---

## 4. Estructura de Clases (propuesta)
- `Sesion`: materia, docente, número de sesión, duración.
- `EstadoHorario`: asignaciones actuales; agregar, remover y consultar ocupación.
- `ValidadorRestricciones`: implementa las restricciones 1 a 5 y la verificación final.
- `AgenteDFS`: búsqueda recursiva y registro de métricas.
- `Metricas`: contadores, retrocesos por nivel y tiempo.
- Módulo de datos: materias, bloques y matriz de ocupaciones (sección 2).

---

## 5. Trazas Manuales (preparación, no entregable)
Dos escenarios reducidos para seguir a mano el árbol de búsqueda, con el mismo orden fijo y las mismas restricciones:
1. **Sin retroceso:** pocas sesiones y bloques, donde la primera rama lleva directamente a la solución.
2. **Con retroceso:** un escenario mínimo donde una ocupación de docente obliga a deshacer al menos una asignación.

Los datos concretos de ambos se definirán junto con la implementación.

---

## 6. Estructura del Entregable Final (Reporte Técnico)
1. **Portada institucional:** materia, corte, integrantes, matrícula y fecha.
2. **Introducción:** problema de horarios como problema de satisfacción de restricciones (CSP) y su formulación como búsqueda en espacio de estados.
3. **Planteamiento del problema:** contexto del plan de estudios, alcance, supuestos y exclusiones.
4. **Especificación del agente:** tabla PEAS y características del entorno.
5. **Modelo de búsqueda:** estado, acciones, restricciones, orden fijo y justificación de búsqueda no informada.
6. **Diseño e implementación:** estructura de clases y explicación del mecanismo recursivo de retroceso.
7. **Resultados:** horario generado para 7° "A", las 6 métricas y una gráfica de retrocesos por nivel del árbol.
8. **Discusión y conclusión:** comportamiento del retroceso frente al tamaño del espacio combinatorio; búsqueda informada (MRV) como trabajo futuro.
9. **Bibliografía.**
