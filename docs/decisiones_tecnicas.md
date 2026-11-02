# Documento de Decisiones Técnicas e Implementación

**Proyecto:** Generación de horarios académicos sin conflictos mediante DFS + Backtracking  
**Materia:** Fundamentos de Inteligencia Artificial  
**Autores:** Ruiz Pérez Brian Luis & Zárate Vázquez Diego Alberto  

---

## 1. Arquitectura Técnica y Lenguaje
- **Lenguaje:** Python 3.10+, orientado a objetos y organizado en módulos (paquete `src`, ejecución con `python -m src.main` desde la raíz).
- **Interfaz visual:** Tkinter (incluido con Python). Requisito de la plantilla: capturas de la ventana con la especificación, la solución y la ejecución paso a paso.
- **Gráficas:** `matplotlib`, con la API de `Figure` (sin ventana). `python -m src.graficas` genera en `salidas/graficas/` los retrocesos por nivel de cada caso y una comparación de los casos.
- **Pruebas:** `unittest` (`python -m unittest` desde la raíz).
- **Descartado:** `pandas` (la tabla del horario se muestra en la interfaz) y una interfaz web (se eligió Tkinter).

---

## 2. Dominio de Datos

### 2.1 Grupo y aula
- **Grupo objetivo:** 7° "A", Ingeniería en Tecnologías de la Información e Innovación Digital.
- **Aula:** el grupo tiene su propia aula (Aula 7A), donde se imparten todas sus clases. El aula no se busca ni se valida: el agente solo decide en qué bloque va cada sesión.

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
- Aulas y laboratorio: fuera del modelo; el grupo siempre ocupa su propia aula.

### 2.5 Matriz de ocupaciones previas de docentes
Bloques en los que cada docente ya imparte clase a otros grupos y, por lo tanto, no está disponible para 7° "A". Es un escenario ficticio pero verosímil, calibrado para que **tenga solución** y **obligue a retroceder**.

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
Conjunto de asignaciones `(sesión, bloque)`, donde `bloque = (día, B1..B4)`. Va de 0 a 18 asignaciones.

### 3.2 Restricciones (validación de cada candidato)
1. **Grupo:** el bloque no está ocupado por otra sesión de 7° "A".
2. **Docente:** el docente de la materia no tiene ese bloque en la matriz de ocupaciones.
3. **Distribución:** la materia no tiene otra sesión ese mismo día.
4. **Orden de sesiones:** para sesiones equivalentes de una materia (todas las de 2 h), la sesión `k` va en un día estrictamente posterior a la sesión `k-1`. En Inglés aplica solo entre `M4.1` y `M4.2`; `M4.3` (1 h) puede ir en cualquier día libre para Inglés.

### 3.3 Orden fijo de búsqueda (búsqueda no informada)
- **Sesiones:** `M1.1, M1.2, M1.3, M2.1, …, M7.2` (orden de la tabla 2.2).
- **Valores:** días de `Lu` a `Vi` y, dentro de cada día, bloques de `B1` a `B4`.
- No se reordenan sesiones ni valores durante la búsqueda (sin MRV, LCV ni forward checking).

### 3.4 Definición de métricas
| Métrica | Definición operativa |
|---|---|
| Validez | El horario final cumple las 4 restricciones (verificación independiente al terminar). |
| Materias asignadas | Materias con todas sus sesiones colocadas (objetivo 7; 18 sesiones). |
| Conflictos finales | Violaciones detectadas por la verificación final (objetivo 0). |
| Estados explorados | Cada candidato `(sesión, bloque)` evaluado por el validador, sea válido o no. |
| Retrocesos | Cada asignación válida que se deshace porque su rama no llevó a solución. Se registra el **nivel** (índice de la sesión, 0–17) donde ocurre. |
| Tiempo de resolución | Tiempo de cómputo de la búsqueda (`time.perf_counter`). |

### 3.5 Pseudocódigo

```python
def dfs(k):                                 # k = índice de la sesión actual (nivel del árbol, 0–17)
    if k == len(sesiones):
        emitir(SOLUCION)
        return True                         # Estado objetivo: 18 sesiones asignadas

    sesion = sesiones[k]
    for bloque in bloques:                  # Lu-B1, Lu-B2, …, Vi-B4 (orden fijo)
        metricas.registrar_exploracion()
        emitir(PROBAR, k, sesion, bloque)
        motivo = validar(escenario, estado, sesion, bloque)   # None si es válida
        if motivo is not None:
            emitir(RECHAZAR, k, sesion, bloque, motivo)
            continue
        estado.agregar(Asignacion(sesion, bloque))            # Actuador: asignar
        emitir(ACEPTAR, k, sesion, bloque)
        if dfs(k + 1):
            return True
        estado.remover(sesion)                                # Actuador: deshacer
        metricas.registrar_retroceso(k)
        emitir(RETROCEDER, k, sesion, bloque)
    return False                            # Ninguna opción válida: la rama falla
```

Si `dfs(0)` devuelve `False`, se emite `SIN_SOLUCION`.

### 3.6 Motivos de rechazo
`validar` devuelve el motivo del **primer** rechazo, revisando en orden R1 → R2 → R3 → R4:

| Motivo | Restricción |
|---|---|
| `BLOQUE_OCUPADO_POR_GRUPO` | R1 |
| `DOCENTE_OCUPADO` | R2 |
| `MATERIA_YA_TIENE_SESION_ESE_DIA` | R3 |
| `VIOLA_ORDEN_DE_SESIONES` | R4 |

El motivo se muestra en la interfaz y se usa en el reporte.

### 3.7 Eventos de la búsqueda
La búsqueda se ejecuta completa **antes** de mostrar la ventana y guarda una lista de eventos (`PROBAR`, `ACEPTAR`, `RECHAZAR`, `RETROCEDER`, `SOLUCION`, `SIN_SOLUCION`), cada uno con nivel, sesión, bloque y motivo. La interfaz los reproduce con `after()`. Así la ventana no se congela y la búsqueda queda separada de la interfaz.

La reproducción vive en `src/reproduccion.py` (clase `Reproductor`), sin dependencias de Tkinter, para poder probarla de forma automática. Aplica los eventos uno por uno, permite avanzar y retroceder, y mantiene el horario parcial, el último paso, los contadores y una bitácora. `src/interfaz.py` solo dibuja ese estado y ofrece los controles: reproducir/pausar, paso anterior y siguiente, reiniciar, ir al final, velocidad de 1 a 2 000 pasos por segundo y atajos de teclado (Espacio, ←, →, Inicio, Fin). Cada paso se marca con texto además de color: PROBANDO, ACEPTADA, RECHAZO con la regla incumplida y RETROCESO.

### 3.8 Resultado de referencia del caso 1
Con los datos del caso 1 (sección 2.5), el agente obtiene:
- Solución encontrada: **sí** (18/18 sesiones, 0 conflictos).
- Estados explorados: **1 834**.
- Retrocesos: **83**, concentrados en los niveles 12 a 16: 1, 3, 16, 21 y 42, en las sesiones de Inglés, Habilidades Gerenciales y Formulación de Proyectos.

| | Lu | Ma | Mi | Ju | Vi |
|---|---|---|---|---|---|
| **B1** 8–10 | M2.1 | M1.2 | M1.3 | M7.1 | M5.2 |
| **B2** 10–12 | M1.1 | M2.2 | M3.3 | M5.1 | M7.2 |
| **B3** 12–14 | M4.1 | M3.2 | M2.3 | M6.1 | M6.2 |
| **B4** 14–16 | M3.1 | M4.2 | M4.3 (1 h) | libre | libre |

Como la búsqueda es determinista, estos valores se reproducen exactamente en cada ejecución. `tests/test_busqueda.py` los verifica como prueba de correctitud.

### 3.9 Tamaño del espacio de estados
La plantilla pide el tamaño y su proceso de cálculo. Se calcula por niveles, agregando restricciones. Todas las cifras se reproducen con `python -m src.espacio_estados`.

| Nivel | Consideración | Horarios completos |
|---|---|---|
| 1 | Cada una de las 18 sesiones en cualquiera de los 20 bloques: $20^{18}$ | 262 144 000 000 000 000 000 000 ≈ 2.62 × 10²³ |
| 2 | + R1 (bloques distintos): $P(20,18) = 20!/2!$ | 1 216 451 004 088 320 000 ≈ 1.22 × 10¹⁸ |
| 3 | + R3 y R4, sin ocupaciones de docentes | 24 156 610 560 000 ≈ 2.4 × 10¹³ |
| 4 | + R2: horarios válidos de cada caso | ver tabla siguiente |

| Caso | Horarios válidos (nivel 4) |
|---|---|
| 1. Base | 149 507 400 888 ≈ 1.5 × 10¹¹ |
| 2. Docente restringido | 24 255 194 220 ≈ 2.4 × 10¹⁰ |
| 3. Séptimos saturados | 116 114 906 919 ≈ 1.2 × 10¹¹ |
| 4. Sin solución | 0 |

- **Cómo se cuentan los niveles 3 y 4.** Es un conteo exacto por programación dinámica que recorre la semana **día por día**:
  - Por R3, cada materia tiene a lo más una sesión por día.
  - Por R4, las sesiones equivalentes de una materia quedan determinadas por el conjunto de días que ocupan.
  - Basta entonces decidir, para cada día, qué materias tienen sesión y contar de cuántas formas caben en bloques distintos y libres para su docente.

  El cálculo tarda alrededor de medio segundo. `tests/test_espacio_estados.py` lo contrasta con una enumeración por fuerza bruta en escenarios reducidos.
- **Cota de estados parciales** (nodos del árbol) con R1: $\sum_{k=0}^{18} P(20,k) \approx 1.75 \times 10^{18}$.
- **Argumento para el reporte:** hay billones de horarios posibles y el DFS encuentra uno válido evaluando 1 834 candidatos (caso 1), porque descarta ramas completas en cuanto detecta un conflicto.

---

## 4. Estructura del Código

```
├── README.md · requirements.txt · .gitignore
├── docs/                    propuesta, decisiones técnicas, borrador, referencias/ (PDF)
├── src/
│   ├── main.py              punto de entrada (python -m src.main)
│   ├── modelo.py            Materia, Sesion, BloqueHorario, Asignacion, EstadoHorario, Escenario
│   ├── escenarios.py        datos de los 4 casos y de los 2 escenarios mini
│   ├── restricciones.py     R1–R4; validar(...) -> MotivoRechazo | None
│   ├── busqueda.py          AgenteDFS, TipoEvento, Evento, Resultado
│   ├── metricas.py          Metricas (explorados, retrocesos por nivel, tiempo)
│   ├── verificacion.py      verificación final independiente (métricas 1–3)
│   ├── reproduccion.py      Reproductor: recorre la traza de eventos (sin Tkinter)
│   ├── interfaz.py          Tkinter; dibuja el estado del reproductor
│   ├── espacio_estados.py   tamaño del espacio de estados por niveles (python -m src.espacio_estados)
│   ├── resultados.py        resumen por caso en salidas/resultados/ (python -m src.resultados)
│   └── graficas.py          gráficas PNG para el reporte (python -m src.graficas)
├── tests/                   pruebas por módulo + reproducción exacta de los casos
└── salidas/                 gráficas y resultados generados (no versionados)
```

Principios:
- **Las reglas viven solo en `restricciones.py`.** `EstadoHorario` solo guarda asignaciones.
- **El estado es `(sesión, bloque)`.** El aula del grupo es un dato descriptivo de `Escenario`.
- **`Materia` guarda las duraciones de sus sesiones** (por ejemplo, `(2, 2, 1)`) y las horas se calculan a partir de ellas.
- **`BloqueHorario` incluye `indice_dia`**, que se necesita para aplicar R4.
- **`Escenario.validar_integridad()` revisa la consistencia de los datos y no su tamaño**, para aceptar los escenarios mini. Rechaza ocupaciones con docentes o bloques inexistentes.
- **`verificacion.py` no reutiliza el validador incremental.** Es una comprobación independiente del resultado.
- **`reproduccion.py` no depende de Tkinter.** La interfaz solo dibuja, así que la lógica de reproducción se prueba de forma automática; las pruebas de la interfaz se omiten si no hay Tkinter o pantalla.

---

## 5. Casos de Resultados
La plantilla exige al menos tres ejemplos **resueltos** y no triviales. Los cuatro casos comparten materias, días y bloques; solo cambian las ocupaciones de los docentes (`src/escenarios.py`). Los resultados están fijados en `tests/test_escenarios.py` y los horarios válidos en `tests/test_espacio_estados.py`. `python -m src.resultados` genera estas tablas en `salidas/resultados/resumen.md`.

| Caso | Escenario | Ocupaciones | Explorados | Retrocesos | Eventos | Horarios válidos | Solución |
|---|---|---|---|---|---|---|---|
| 1. Base | Ocupaciones moderadas (sección 2.5) | 31 | 1 834 | 83 | 3 752 | 149 507 400 888 | sí |
| 2. Docente restringido | Como el base, pero D6 (Formulación) **solo puede martes y jueves** | 39 | 10 611 | 522 | 21 745 | 24 255 194 220 | sí |
| 3. Séptimos saturados | Cada docente da su materia también a 7° B y 7° C | 36 | 692 | 26 | 1 411 | 116 114 906 919 | sí |
| 4. Sin solución | Como el base, pero D1 (IA) **solo puede martes y jueves** | 38 | 500 | 24 | 1 025 | 0 | no |

Retrocesos por nivel (nivel = índice de la sesión, 0–17):

| Caso | Retrocesos por nivel |
|---|---|
| 1 | 12: 1 · 13: 3 · 14: 16 · 15: 21 · 16: 42 |
| 2 | 10: 1 · 11: 9 · 12: 55 · 13: 97 · 14: 284 · 15: 19 · 16: 57 |
| 3 | 13: 2 · 14: 8 · 15: 6 · 16: 10 |
| 4 | 0: 8 · 1: 16 |

### 5.1 Cómo se obtuvieron
- **Caso 2.** Se probaron patrones de disponibilidad que se pueden explicar ("solo ciertos días", "solo mañanas", etc.) para D5, D6 y D7. Se eligió D6 solo martes y jueves porque los retrocesos (6 veces los del caso 1) suben hasta el nivel 10, y porque la traza sigue siendo manejable para la animación. La variante "solo lunes y viernes" produce 1 783 retrocesos y 73 454 eventos.
- **Caso 3.** Se generaron horarios válidos completos para 7° B y 7° C con los mismos docentes y sin choques entre ellos. Los bloques que ocupan pasan a ser las ocupaciones de 7° A, así que cada docente queda ocupado el doble de sesiones de su materia. En 300 combinaciones generadas, todas tuvieron solución, con 26 retrocesos como máximo; se eligió la de más retrocesos.
- **Caso 4.** IA es la primera materia del orden y necesita 3 sesiones en días distintos (R3). Con D1 disponible solo 2 días no hay solución, y el agente lo demuestra rápido porque la falla ocurre en los niveles 0 y 1.

### 5.2 Hallazgo para la discusión
Se esperaba que el caso 3, con más ocupaciones, fuera el más difícil. **No lo fue.**
- **Caso 3:** 36 ocupaciones y 26 retrocesos.
- **Caso 2:** 39 ocupaciones y 522 retrocesos.

La diferencia está en **dónde** caen las restricciones respecto al orden fijo de búsqueda:
- En el caso 3 están repartidas entre todos los docentes, así que el agente descarta antes las opciones malas.
- En el caso 2 se concentran en una materia que se programa casi al final, y el agente descubre el conflicto tarde, después de haber construido mucho horario que luego tiene que deshacer.

El conteo de horarios válidos (sección 3.9) lo confirma: el caso 3 conserva unos 116 mil millones de horarios válidos, casi 5 veces los del caso 2 (unos 24 mil millones), a pesar de tener casi las mismas ocupaciones.

La figura `salidas/graficas/comparacion_casos.png` muestra este contraste en paneles separados, cada uno con su propio eje: ocupaciones, estados explorados, retrocesos y horarios válidos.

Esto ilustra la limitación central de la búsqueda no informada: el orden en que se recorre el problema no aprovecha lo que ya se sabe de las restricciones. Es justo lo que corregiría una heurística como MRV (empezar por la sesión con menos opciones), que queda como trabajo futuro.

---

## 6. Trazas Manuales (preparación, no entregable)
Dos escenarios reducidos (`ESCENARIOS_MINI` en `src/escenarios.py`) para seguir a mano el árbol de búsqueda, con el mismo orden fijo y las mismas restricciones:
- 2 materias: M1 con dos sesiones (D1) y M2 con una sesión (D2).
- 2 días (Lu, Ma) con 2 bloques cada uno (B1, B2).

| Escenario | Ocupaciones | Explorados | Retrocesos | Pasos (eventos) | Solución |
|---|---|---|---|---|---|
| Mini A — Sin retroceso | ninguna | 6 | 0 | 13 | M1.1 Lu-B1 · M1.2 Ma-B1 · M2.1 Lu-B2 |
| Mini B — Con retroceso | D2 ocupado en Lu-B2 y Ma-B2 | 12 | 1 | 26 | M1.1 Lu-B1 · M1.2 Ma-B2 · M2.1 Ma-B1 |

En el Mini B, M2.1 no cabe con M1.2 en Ma-B1: los bloques B1 están ocupados por el grupo y los B2 por el docente. El agente deshace M1.2, la mueve a Ma-B2 y entonces M2.1 entra en Ma-B1. La secuencia completa de pasos de ambos escenarios está fijada en `tests/test_escenarios.py`, para comparar con la traza hecha a mano. Ambos se pueden elegir en el selector de la interfaz y seguir paso a paso.

---

## 7. Estructura del Reporte (plantilla LaTeX de la materia)
1. **Planteamiento del problema:** explícito y detallado (de las secciones con más peso). Contexto del plan de estudios, alcance y exclusiones.
2. **PEAS:** medida de desempeño, entorno con la tabla de 7 características justificadas, actuadores y sensores. Cada uno enunciado, explicado y justificado.
3. **Especificación del problema de búsqueda.**
4. **Estado inicial:** 2 o 3 ejemplos explicados, tomados de los casos.
5. **Meta:** 2 o 3 ejemplos explicados.
6. **Espacio de estados:** tamaño y cálculo (sección 3.9) y ejemplos de estados importantes.
7. **Transiciones:** orden de análisis de las ramas (sección 3.3) y tabla de transiciones con ejemplos.
8. **Métricas de rendimiento:** enunciadas, explicadas y justificadas.
9. **Heurísticas:** "No aplica", justificado; MRV como trabajo futuro.
10. **Resultados:** casos 1–3 (y 4 opcional). Para cada uno: descripción, estado inicial y meta, solución, ejecución paso a paso y comentarios, con capturas **solo de la ventana** de la interfaz (o un video).
    - Tablas: `salidas/resultados/resumen.md` (`python -m src.resultados`).
    - Figuras: `retrocesos_<caso>.png` en los comentarios de cada caso y `comparacion_casos.png` en la discusión (`python -m src.graficas`).

Regla de la plantilla: **toda figura, tabla, fórmula o cita debe referenciarse en el texto**; se penaliza si no.
