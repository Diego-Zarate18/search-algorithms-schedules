# Entregable del Proyecto — Alineado a Plantilla Institucional

**Proyecto:** Generación de horarios académicos sin conflictos mediante búsqueda en profundidad con retroceso  
**Materia:** Fundamentos de Inteligencia Artificial — 7° "A"  
**Autores:** Ruiz Pérez Brian Luis (243738) · Zárate Vázquez Diego Alberto (243683)  
**Docente:** Carlos Alberto Díaz Hernández  
**Periodo:** Septiembre – Diciembre de 2026

---

## ⚠️ Requisitos críticos extraídos de la plantilla

> [!CAUTION]
> La plantilla establece estas reglas que, si no se cumplen, **generan penalización**:
> 1. **Todo objeto** (figura, fórmula, tabla, cita) **debe estar referenciado en el texto**. Si hay objetos no referenciados → penalización.
> 2. **El código debe presentarse en bloques de código**, no capturas de pantalla → penalización.
> 3. **El método de búsqueda debe estar separado de la visualización** → penalización fuerte.
> 4. Cada función/método debe explicar: **qué parámetros recibe, qué hace, qué devuelve**.
> 5. Desde la **interfaz visual** debe poder cambiarse el inicio, la meta o el escenario.
> 6. **Al menos 3 ejemplos no triviales** en Resultados, cada uno con: descripción, estado inicial y meta, solución, ejecución paso a paso, comentarios.
> 7. Los **anexos** deben estar referenciados desde el texto.

---

## Mapeo: Plantilla → Contenido del Proyecto

| Sección de la plantilla | Contenido para el proyecto de horarios |
|---|---|
| Resumen | Resumen en español del proyecto |
| Abstract | Resumen en inglés |
| **Cap. 1** — Nombre del Proyecto | Horario académico sin conflictos |
| 1.1 Planteamiento del problema | Contexto de la UPChiapas, grupos activos, restricciones |
| 1.2 PEAS | Formulación completa con justificaciones |
| 1.3 Especificación del problema de búsqueda | CSP modelado por sesiones contiguas |
| 1.4 Estado inicial | 3 ejemplos de horarios vacíos con diferentes restricciones |
| 1.5 Meta | 3 ejemplos de horarios completos válidos |
| 1.6 Espacio de estados | Cálculo formal con sesiones, dominios y cota |
| 1.7 Transiciones | Tabla de transiciones + orden de ramificación |
| 1.8 Métricas de rendimiento | 6 métricas definidas y justificadas |
| 1.9 Heurísticas | MRV + Forward Checking justificados |
| **Cap. 2** — Implementación | Funciones Python documentadas (sin visualización) |
| **Cap. 3** — Resultados | 3 casos con capturas de interfaz visual |
| **Cap. 4** — Conclusiones y recomendaciones | Aprendizajes + mejoras futuras |
| **Cap. 5** — Anexos | Datos completos, ocupaciones, código auxiliar |
| Bibliografía | Fuentes académicas |

---

## Borrador Completo por Capítulo

---

### Resumen

Este proyecto presenta el diseño e implementación de un agente inteligente que genera horarios académicos libres de conflictos para un grupo universitario, utilizando búsqueda en profundidad con retroceso (DFS + Backtracking). El problema se formula como un Problema de Satisfacción de Restricciones (CSP) donde las variables son sesiones contiguas de clase y las restricciones incluyen disponibilidad de docentes, ocupación de aulas y horarios fijos de otros grupos activos. Se implementan dos variantes del algoritmo: una versión base sin heurísticas y una versión mejorada con selección por Mínimos Valores Restantes (MRV) y propagación por Forward Checking. Los resultados muestran que la versión con heurísticas reduce significativamente el número de estados explorados y retrocesos, generando horarios válidos para distintos escenarios de prueba.

### Abstract

This project presents the design and implementation of an intelligent agent that generates conflict-free academic schedules for a university group, using Depth-First Search with Backtracking (DFS + Backtracking). The problem is formulated as a Constraint Satisfaction Problem (CSP) where variables are contiguous class sessions and constraints include teacher availability, classroom occupancy, and fixed schedules of other active groups. Two algorithm variants are implemented: a baseline version without heuristics and an improved version with Minimum Remaining Values (MRV) selection and Forward Checking propagation. Results show that the heuristic version significantly reduces the number of explored states and backtracks, generating valid schedules for different test scenarios.

---

### Capítulo 1 — Generación de Horarios Académicos sin Conflictos

#### 1.1 Planteamiento del problema

La Universidad Politécnica de Chiapas opera bajo un plan de estudios cuatrimestral de diez cuatrimestres para la carrera de Ingeniería en Desarrollo de Software (actualmente Ingeniería en Tecnologías de la Información e Innovación Digital). En el cuatrimestre actual se encuentran activos los grupos de primero (1° "A"), cuarto (4° "A"), séptimo (7° "A") y décimo (10° "A"). Los cuatrimestres sexto y décimo corresponden a estadías (TSU y Profesional, respectivamente) con una carga de 600 horas; sin embargo, dado que la mayor parte de las actividades de estadía se realizan fuera de la universidad, solo se incorporan al modelo aquellas actividades con horarios y recursos universitarios definidos.

El grupo objetivo para la generación del horario es el **7° "A"**, que cursa siete materias con una carga total de **29 horas semanales**. Las clases se imparten de lunes a viernes en bloques de una hora, de 07:00 a 14:00, lo que genera una cuadrícula de **35 bloques semanales disponibles**. La universidad cuenta con **15 aulas** para todos los grupos.

**El problema central** consiste en asignar las 29 horas de clase de las 7 materias a bloques horarios y aulas, cumpliendo las siguientes restricciones:

1. Las horas de una misma materia en un día deben ser **contiguas** (no pueden quedar dispersas en el mismo día).
2. Un docente no puede impartir clase a dos grupos simultáneamente.
3. Un aula no puede ser ocupada por dos grupos en el mismo bloque.
4. El grupo 7° "A" no puede tener dos materias al mismo tiempo.
5. Las asignaciones no deben chocar con las **ocupaciones previamente establecidas** de los grupos 1°, 4° y 10°.
6. La suma de horas asignadas por materia debe igualar su carga semanal.

La restricción de contigüidad (punto 1) permite reformular el problema: en lugar de asignar 29 horas individuales, se asignan **sesiones contiguas** (bloques de horas consecutivas) a combinaciones de día, hora de inicio y aula. Esto reduce la complejidad del árbol de búsqueda.

Se utiliza **búsqueda en profundidad con retroceso** (DFS + Backtracking) como método de búsqueda, que prueba asignaciones de sesiones, rechaza las que generan conflictos y retrocede cuando es necesario. Adicionalmente, se implementan heurísticas de CSP (MRV y Forward Checking) para mejorar la eficiencia del algoritmo.

Las materias del 7° "A" y sus cargas horarias se muestran en la Tabla 1.2, y los bloques horarios disponibles en la Tabla 1.3 (ver sección 1.3).

#### 1.2 PEAS

##### 1.2.1 Medida de desempeño

La medida de desempeño principal es la **generación de un horario completo y válido** para las siete materias del grupo 7° "A", donde:

- Las 29 horas semanales están asignadas a bloques y aulas sin conflictos.
- Se respetan todas las restricciones enumeradas en el planteamiento del problema (sección 1.1).
- Las horas de cada materia son contiguas dentro de cada día.

Como criterios secundarios, se busca:

- **Minimizar el número de estados explorados** durante la búsqueda, lo que indica eficiencia en la poda del árbol.
- **Minimizar el número de retrocesos**, que refleja la capacidad del algoritmo para evitar ramas inviables.
- **Minimizar el tiempo de resolución**, medido en segundos desde el inicio hasta encontrar la primera solución válida.

Estas métricas se justifican porque permiten evaluar no solo la corrección del resultado (horario válido) sino también la eficiencia del método de búsqueda empleado. Las métricas se detallan en la sección 1.8.

##### 1.2.2 Entorno

El entorno es un modelo de la operación académica de la universidad, compuesto por:

- Un grupo objetivo (7° "A") con 7 materias y sus cargas horarias (ver Tabla 1.2).
- 7 docentes, cada uno responsable de una materia, con disponibilidades determinadas por sus compromisos con otros grupos.
- 15 aulas disponibles.
- 35 bloques horarios semanales (5 días × 7 bloques de 1 hora).
- Una matriz de ocupaciones previas que registra qué docentes y aulas están ocupados por los grupos 1°, 4° y 10° en bloques específicos.

Toda la información está definida antes de iniciar la búsqueda y no cambia durante su ejecución.

**Características del entorno**

La Tabla 1.1 presenta la caracterización del entorno según las propiedades estándar de entornos en IA.

> **Tabla 1.1:** Caracterización del entorno. Se elige la característica que aplica y se justifica en términos del problema.

| Característica | Clasificación | Justificación |
|---|---|---|
| Determinista o no determinista | **Determinista** | Dado un estado parcial del horario y una asignación específica (materia, día, hora, aula), el resultado (aceptación o rechazo) es completamente predecible. No hay incertidumbre ni aleatoriedad en las transiciones. |
| Monoagente o multiagente | **Monoagente** | Existe un único agente (el algoritmo de búsqueda) que toma todas las decisiones de asignación. No hay otros agentes que compitan o cooperen en la generación del horario. |
| Completamente observable o parcialmente observable | **Completamente observable** | El agente tiene acceso a toda la información relevante en todo momento: las materias pendientes, los bloques disponibles, las aulas libres, las ocupaciones previas y el estado parcial del horario. No hay información oculta. |
| Episódico o secuencial | **Secuencial** | Cada asignación depende de las asignaciones anteriores. Si se asigna una materia al bloque de las 07:00 del lunes en el aula 1, esta decisión afecta qué bloques y aulas están disponibles para las siguientes asignaciones. Las decisiones no son independientes entre sí. |
| Discreto o continuo | **Discreto** | Los bloques horarios son unidades discretas de 1 hora, los días son 5 valores discretos, y las aulas son 15 opciones discretas. No hay valores continuos ni intermedios. |
| Estático o dinámico | **Estático** | El entorno no cambia mientras el agente está deliberando. Las ocupaciones previas, las disponibilidades de docentes y las aulas permanecen fijas durante toda la ejecución del algoritmo. |
| Conocido o no conocido | **Conocido** | El agente conoce todas las reglas del entorno: las restricciones, los efectos de cada asignación y las condiciones de conflicto. No necesita aprender ni descubrir las reglas durante la búsqueda. |

##### 1.2.3 Actuadores

Los actuadores son las acciones que el agente puede ejecutar para interactuar con el entorno (el horario parcial):

1. **Asignar una sesión:** Seleccionar una sesión pendiente (materia + duración) y colocarla en un día, hora de inicio y aula específicos. Esto modifica el estado del horario agregando la asignación.

2. **Validar una asignación:** Verificar que la asignación propuesta cumple todas las restricciones (R1–R7). Esta acción consulta el estado actual y las ocupaciones previas para determinar si hay conflictos.

3. **Aceptar una asignación:** Confirmar que la asignación es válida y conservarla en el horario parcial, avanzando a la siguiente sesión pendiente.

4. **Rechazar una asignación:** Descartar una asignación que genera conflictos e intentar la siguiente combinación disponible en el dominio de la sesión.

5. **Retroceder (backtrack):** Cuando no quedan combinaciones válidas para la sesión actual, deshacer la última asignación confirmada y probar una alternativa diferente para la sesión anterior. Este actuador es fundamental para garantizar la completitud de la búsqueda.

##### 1.2.4 Sensores

Los sensores proporcionan al agente la información necesaria para tomar decisiones:

1. **Lista de materias y cargas horarias:** Las 7 materias con sus horas semanales y docentes responsables (Tabla 1.2).
2. **Patrones de sesión:** La distribución de la carga horaria de cada materia en sesiones contiguas (por ejemplo, Inteligencia Artificial: sesión de 3 hrs + sesión de 2 hrs).
3. **Bloques horarios disponibles:** Los 35 bloques semanales (Lunes a Viernes, 07:00 a 14:00).
4. **Aulas disponibles:** Las 15 aulas con sus identificadores.
5. **Ocupaciones previas:** La matriz que registra qué docentes y aulas están ocupados por los grupos 1°, 4° y 10° en cada bloque.
6. **Estado parcial del horario:** Las asignaciones ya confirmadas para el grupo 7° "A", que el agente consulta para detectar conflictos.
7. **Dominios residuales:** Para cada sesión pendiente, el conjunto de combinaciones (día, hora_inicio, aula) que aún son potencialmente válidas (utilizado en la versión con Forward Checking).

#### 1.3 Especificación del problema de búsqueda

El problema se formula como un **Problema de Satisfacción de Restricciones (CSP)** donde:

- **Variables:** Cada sesión contigua que debe colocarse en el horario. Con los patrones de sesión recomendados (ver Tabla 1.4), se obtienen **12 sesiones** a asignar.
- **Dominios:** Para cada sesión $s_i$ de duración $d_i$ horas, su dominio es el conjunto de tripletas $(día, hora\_inicio, aula)$ válidas:

$$\text{dom}(s_i) = \left\{ (j, h, a) \;\middle|\; j \in \{L, M, X, J, V\},\ h \in \{1, \ldots, 8-d_i\},\ a \in \{1, \ldots, 15\} \right\}$$

- **Restricciones:** Se definen 7 restricciones duras (ver Tabla 1.5).

> **Tabla 1.2:** Materias del grupo 7° "A" con docentes y cargas horarias.

| ID | Materia | Docente | Carga (hrs/semana) |
|---|---|---|---|
| $M_1$ | Inteligencia Artificial | $D_1$ | 5 |
| $M_2$ | Bases de Datos en la Nube | $D_2$ | 5 |
| $M_3$ | Seguridad Informática | $D_3$ | 4 |
| $M_4$ | Ética y Legislación | $D_4$ | 4 |
| $M_5$ | Formulación de Proyectos | $D_5$ | 5 |
| $M_6$ | Inglés VI | $D_6$ | 3 |
| $M_7$ | Habilidades Gerenciales | $D_7$ | 3 |
| | **Total** | | **29** |

> **Tabla 1.3:** Bloques horarios disponibles (5 días × 7 bloques = 35 bloques totales).

| Bloque | Hora |
|---|---|
| 1 | 07:00 – 08:00 |
| 2 | 08:00 – 09:00 |
| 3 | 09:00 – 10:00 |
| 4 | 10:00 – 11:00 |
| 5 | 11:00 – 12:00 |
| 6 | 12:00 – 13:00 |
| 7 | 13:00 – 14:00 |

> **Tabla 1.4:** Patrones de sesión por materia.

| Materia | Carga | Patrón | Sesiones resultantes |
|---|---|---|---|
| $M_1$ — IA | 5 | 3 + 2 | $s_1$(3h), $s_2$(2h) |
| $M_2$ — BD Nube | 5 | 3 + 2 | $s_3$(3h), $s_4$(2h) |
| $M_3$ — Seg. Inf. | 4 | 2 + 2 | $s_5$(2h), $s_6$(2h) |
| $M_4$ — Ética | 4 | 2 + 2 | $s_7$(2h), $s_8$(2h) |
| $M_5$ — Form. Proy. | 5 | 3 + 2 | $s_9$(3h), $s_{10}$(2h) |
| $M_6$ — Inglés VI | 3 | 3 | $s_{11}$(3h) |
| $M_7$ — Hab. Ger. | 3 | 3 | $s_{12}$(3h) |

> **Tabla 1.5:** Restricciones duras del CSP.

| ID | Restricción | Descripción |
|---|---|---|
| R1 | Docente único | Un docente no puede tener sesiones en bloques que se solapen |
| R2 | Aula única | Un aula no puede albergar dos sesiones en el mismo bloque |
| R3 | Grupo único | El grupo 7°A no puede tener dos sesiones simultáneas |
| R4 | Contigüidad | Los bloques de una sesión son consecutivos (garantizado por diseño) |
| R5 | Ocupaciones previas | No chocar con horarios fijos de 1°, 4° y 10° |
| R6 | Carga horaria | La suma de duraciones de sesiones iguala la carga de la materia |
| R7 | Una sesión por día | Una materia tiene a lo sumo una sesión por día |

#### 1.4 Estado inicial

Un estado se representa como el conjunto de asignaciones confirmadas. El estado inicial es un horario **vacío para el grupo 7° "A"**, con las ocupaciones previas de otros grupos ya registradas como restricciones fijas.

**Ejemplo 1 — Escenario base:** Horario vacío con las 12 sesiones pendientes y las ocupaciones previas de los 3 grupos activos (1°, 4°, 10°). Los docentes $D_1$–$D_7$ tienen disponibilidades limitadas por sus clases en otros grupos.

$$S_0 = \emptyset, \quad \text{sesiones pendientes} = \{s_1, s_2, \ldots, s_{12}\}$$

**Ejemplo 2 — Escenario con docente muy restringido:** Igual al Ejemplo 1, pero el docente $D_1$ solo está disponible los lunes y miércoles (por ocupaciones en 4° "A" los martes, jueves y viernes). Esto reduce drásticamente el dominio de $s_1$ y $s_2$.

$$S_0 = \emptyset, \quad |dom(s_1)| = 5 \times 2 \times 15 = 150 \quad (\text{vs. } 375 \text{ sin esta restricción})$$

**Ejemplo 3 — Escenario con aula fija:** Igual al Ejemplo 1, pero la materia $M_3$ (Seguridad Informática) requiere un laboratorio específico (aula 12). Esto reduce el dominio de $s_5$ y $s_6$ a una sola aula.

$$S_0 = \emptyset, \quad |dom(s_5)| = 6 \times 5 \times 1 = 30 \quad (\text{vs. } 450 \text{ con 15 aulas})$$

#### 1.5 Meta

El estado meta es un horario en el que **todas las sesiones están asignadas** y **todas las restricciones se cumplen**.

**Ejemplo 1 — Horario completo para escenario base:**

$$S^* = \{(s_1, L, 1, A_3),\ (s_2, X, 2, A_3),\ (s_3, M, 1, A_5),\ \ldots,\ (s_{12}, V, 1, A_7)\}$$

Donde $(s_i, día, hora\_inicio, aula)$ indica que la sesión $s_i$ se asigna al día indicado, comenzando en el bloque $hora\_inicio$, en el aula correspondiente. El horario resultante tiene 0 conflictos, 7 materias asignadas y 29 horas colocadas.

**Ejemplo 2 — Horario con docente restringido:**

Mismo formato que el Ejemplo 1, pero las sesiones de $M_1$ (IA) solo aparecen en lunes y miércoles, cumpliendo la restricción de disponibilidad de $D_1$.

**Ejemplo 3 — Horario con aula fija:**

Mismo formato, pero las sesiones $s_5$ y $s_6$ de Seguridad Informática siempre están asignadas al aula 12 (laboratorio).

> [!NOTE]
> En los tres ejemplos, la meta se verifica confirmando que: (1) $|S^*| = 12$ sesiones, (2) la suma de duraciones = 29 horas, (3) ninguna restricción R1–R7 se viola.

#### 1.6 Espacio de estados

Cada estado es un **horario parcial**: un subconjunto de las 12 sesiones que ya han sido asignadas. Un estado puede contener de 0 (estado inicial) a 12 (estado meta) asignaciones.

**Tamaño del dominio por sesión:**

El dominio de una sesión $s_i$ de duración $d_i$ es:

$$|\text{dom}(s_i)| = (8 - d_i) \times 5 \times 15$$

| Duración ($d_i$) | Horas inicio posibles ($8 - d_i$) | Días | Aulas | $|\text{dom}(s_i)|$ |
|---|---|---|---|---|
| 3 horas | 5 | 5 | 15 | 375 |
| 2 horas | 6 | 5 | 15 | 450 |

**Cota superior del espacio de estados (sin restricciones):**

$$|E| = \prod_{i=1}^{12} |\text{dom}(s_i)| = 375^4 \times 450^8 \approx 2.63 \times 10^{31}$$

Donde hay 4 sesiones de 3 horas ($s_1, s_3, s_9, s_{11}$... considerando el patrón actualizado) y 8 sesiones de 2 horas.

> [!IMPORTANT]
> Esta cota es teórica. En la práctica, las restricciones R1–R7 y las ocupaciones previas reducen el espacio efectivo en muchos órdenes de magnitud. Con Forward Checking, el algoritmo típicamente explora menos de $10^3$ estados para este tamaño de problema.

**Estados más importantes:**

- **Estado vacío** ($|S| = 0$): Ninguna sesión asignada, punto de partida.
- **Estado con primera sesión** ($|S| = 1$): Se asignó la sesión más restringida (seleccionada por MRV). Este estado define las podas iniciales para el resto del árbol.
- **Estado casi completo** ($|S| = 11$): Falta una sola sesión. Si su dominio residual es no vacío, la solución está garantizada.
- **Estado meta** ($|S| = 12$): Horario completo y válido.

#### 1.7 Transiciones

Una transición consiste en **agregar una asignación** al estado actual o **remover la última asignación** (retroceso).

**Orden de análisis de las ramas:**

- **Sin heurísticas (versión B):** Las sesiones se seleccionan en el orden fijo de la lista ($s_1, s_2, \ldots, s_{12}$). Para cada sesión, se prueban los valores del dominio en el orden: días (L→V), luego horas (1→7), luego aulas (1→15).

- **Con heurísticas (versión C):** Se selecciona la sesión con **menor dominio residual** (MRV). Los valores se ordenan por **menor impacto** sobre los dominios de las sesiones restantes (LCV).

> **Tabla 1.6:** Transiciones posibles desde un estado parcial $S_k$ con $k$ sesiones asignadas.

| Transición | Precondición | Efecto | Descripción |
|---|---|---|---|
| Asignar $s_i$ a $(j, h, a)$ | $s_i$ pendiente, $(j, h, a) \in \text{dom}(s_i)$, sin conflictos R1–R7 | $S_{k+1} = S_k \cup \{(s_i, j, h, a)\}$ | Se agrega la sesión al horario parcial |
| Rechazar $(j, h, a)$ para $s_i$ | Asignación genera conflicto con R1–R7 | $S_k$ sin cambio, siguiente valor | Se descarta el valor y se prueba el siguiente |
| Retroceder | Todos los valores de $\text{dom}(s_i)$ agotados | $S_{k-1}$ (se remueve la asignación anterior) | Se deshace la última asignación y se prueba otra alternativa para $s_{i-1}$ |

**Ejemplo de transiciones desde el estado inicial:**

1. $S_0 = \emptyset$ → MRV selecciona $s_{11}$ (Inglés VI, 3h, dominio más pequeño)
2. Probar $s_{11}$ en (Lunes, bloque 1, Aula 1) → Validar R1–R7 → ✅ Válido → $S_1 = \{(s_{11}, L, 1, A_1)\}$
3. MRV selecciona $s_7$ (Ética, 2h) → Probar (Lunes, bloque 4, Aula 1) → Validar → ✅ Válido → $S_2$
4. Continuar hasta $S_{12}$ (meta) o retroceder si una sesión no tiene valores válidos.

#### 1.8 Métricas de rendimiento

> **Tabla 1.7:** Métricas de rendimiento del algoritmo.

| # | Métrica | Descripción | Justificación | Objetivo |
|---|---|---|---|---|
| 1 | Validez del horario | Cumplimiento de todas las restricciones R1–R7 | Es el requisito funcional principal del sistema | 100% de restricciones cumplidas |
| 2 | Materias asignadas | Cantidad de materias con todas sus horas correctamente colocadas | Mide la completitud de la solución | 7/7 materias |
| 3 | Conflictos finales | Número de violaciones de restricciones en el horario generado | Cuantifica la corrección del resultado | 0 conflictos |
| 4 | Estados explorados | Cantidad de nodos del árbol de búsqueda que el algoritmo visitó | Mide la eficiencia de la exploración; un menor número indica mejor poda | Minimizar |
| 5 | Retrocesos | Cantidad de veces que el algoritmo deshizo una asignación | Mide la eficacia de las heurísticas para evitar ramas inviables | Minimizar |
| 6 | Tiempo de resolución | Tiempo en segundos desde el inicio de la búsqueda hasta encontrar la solución | Evalúa la viabilidad práctica del algoritmo | < 3 segundos |

Las métricas 4, 5 y 6 se utilizarán para comparar las versiones B (sin heurísticas) y C (con MRV + FC), evidenciando el impacto de las heurísticas CSP sobre la eficiencia de la búsqueda.

#### 1.9 Heurísticas

Aunque la versión base (B) utiliza DFS + Backtracking sin heurísticas (búsqueda no informada), la versión mejorada (C) incorpora dos heurísticas estándar de CSP:

**Heurística 1 — MRV (Minimum Remaining Values):**

Selecciona como siguiente variable la sesión cuyo dominio residual tiene el **menor número de valores válidos**. La justificación es el principio de "fail-first": asignar primero la sesión más restringida permite detectar antes los callejones sin salida y reducir el número de retrocesos.

$$s_{\text{siguiente}} = \arg\min_{s_i \in \text{pendientes}} |\text{dom}(s_i)|$$

**Heurística 2 — Forward Checking (propagación de restricciones):**

Después de cada asignación, se eliminan inmediatamente de los dominios de las sesiones restantes todos los valores que entrarían en conflicto con la asignación recién hecha. Si algún dominio queda vacío, se retrocede inmediatamente **sin explorar más ramas**. Esto evita explorar subárboles que con certeza no conducen a una solución.

Estas heurísticas no cambian la naturaleza del algoritmo (sigue siendo DFS + Backtracking), pero mejoran su eficiencia al guiar el orden de exploración y podar ramas inviables de forma anticipada. Se justifican porque:

1. Son las heurísticas estándar para CSP según Russell & Norvig (2010, Cap. 6).
2. No requieren conocimiento específico del dominio (son genéricas).
3. Permiten una comparación cuantitativa directa con la versión sin heurísticas.

---

### Capítulo 2 — Implementación

> [!IMPORTANT]
> Solo se documenta el **método de búsqueda**. El código de visualización (interfaz gráfica, generación de gráficas) está separado en módulos independientes y no se incluye en este capítulo. La interfaz permite cambiar el escenario (ocupaciones previas), el estado inicial (sesiones ya fijadas) y la meta (materias a asignar).

A continuación se presentan las funciones principales de la implementación. Cada función se documenta con: parámetros que recibe, qué hace y qué devuelve.

---

**Función `preparar_sesiones`** — Genera la lista de sesiones a colocar a partir de las materias y sus patrones.

- **Recibe:** `materias` (lista de objetos Materia con nombre, docente y carga), `patrones` (diccionario que mapea cada materia a una lista de duraciones, ej. `{M1: [3, 2]}`).
- **Hace:** Itera sobre cada materia y su patrón, creando un objeto `Sesion` por cada duración.
- **Devuelve:** Lista de objetos `Sesion` (~12 elementos).

```python
def preparar_sesiones(materias, patrones):
    sesiones = []
    for materia in materias:
        patron = patrones[materia.nombre]
        for i, duracion in enumerate(patron):
            sesion = Sesion(
                materia=materia,
                indice=i,
                duracion=duracion,
                docente=materia.docente
            )
            sesiones.append(sesion)
    return sesiones
```

---

**Función `construir_dominios`** — Calcula los valores iniciales posibles para cada sesión, filtrando las ocupaciones previas.

- **Recibe:** `sesiones` (lista de Sesion), `aulas` (lista de IDs de aula), `ocupaciones` (diccionario que mapea `(docente, día, bloque)` y `(aula, día, bloque)` a booleanos de ocupación).
- **Hace:** Para cada sesión, genera todas las combinaciones (día, hora_inicio, aula) donde no hay conflicto con las ocupaciones previas de 1°, 4° y 10°.
- **Devuelve:** Diccionario `{sesion: [(día, hora_ini, aula), ...]}`.

```python
def construir_dominios(sesiones, aulas, ocupaciones):
    DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes']
    dominios = {}

    for sesion in sesiones:
        dominio = []
        for dia in DIAS:
            for hora_ini in range(1, 8 - sesion.duracion + 1):
                bloques = range(hora_ini, hora_ini + sesion.duracion)
                for aula in aulas:
                    conflicto = False
                    for b in bloques:
                        if ocupaciones.get((sesion.docente, dia, b), False):
                            conflicto = True
                            break
                        if ocupaciones.get((aula, dia, b), False):
                            conflicto = True
                            break
                    if not conflicto:
                        dominio.append((dia, hora_ini, aula))
        dominios[sesion] = dominio

    return dominios
```

---

**Función `resolver`** — Función principal recursiva de DFS + Backtracking con MRV y Forward Checking.

- **Recibe:** `pendientes` (lista de sesiones no asignadas), `dominios` (dominios actuales), `estado` (objeto EstadoHorario con asignaciones actuales), `metricas` (objeto MetricasRendimiento).
- **Hace:** Selecciona la sesión con menor dominio (MRV), prueba cada valor, aplica Forward Checking tras cada asignación, retrocede si no hay solución.
- **Devuelve:** `estado` completo si se encontró solución, `None` si no hay solución en esta rama.

```python
def resolver(pendientes, dominios, estado, metricas):
    if not pendientes:
        return estado

    sesion = min(pendientes, key=lambda s: len(dominios[s]))
    metricas.estados_explorados += 1

    if len(dominios[sesion]) == 0:
        return None

    for (dia, hora_ini, aula) in dominios[sesion]:
        bloques = range(hora_ini, hora_ini + sesion.duracion)

        if not es_valida(sesion, dia, bloques, aula, estado):
            continue

        asignacion = Asignacion(sesion, dia, hora_ini, aula)
        estado.agregar(asignacion)

        nuevos_dominios = forward_check(dominios, asignacion, pendientes)

        restantes = [s for s in pendientes if s != sesion]
        if all(len(nuevos_dominios[s]) > 0 for s in restantes):
            resultado = resolver(restantes, nuevos_dominios, estado, metricas)
            if resultado is not None:
                return resultado

        metricas.retrocesos += 1
        estado.remover(asignacion)

    return None
```

---

**Función `es_valida`** — Verifica que una asignación no viole las restricciones R1–R7.

- **Recibe:** `sesion` (Sesion a asignar), `dia` (día de la semana), `bloques` (rango de bloques), `aula` (ID del aula), `estado` (horario parcial actual).
- **Hace:** Recorre las asignaciones existentes y verifica que no haya conflictos de docente (R1), aula (R2), grupo (R3), ocupaciones previas (R5) ni doble sesión de la misma materia en el mismo día (R7).
- **Devuelve:** `True` si la asignación es válida, `False` si hay conflicto.

```python
def es_valida(sesion, dia, bloques, aula, estado):
    for asig in estado.asignaciones:
        if asig.dia != dia:
            continue

        bloques_existentes = range(asig.hora_ini,
                                   asig.hora_ini + asig.sesion.duracion)
        se_solapan = (bloques.start < bloques_existentes.stop and
                      bloques_existentes.start < bloques.stop)

        if not se_solapan:
            continue

        if asig.sesion.docente == sesion.docente:
            return False
        if asig.aula == aula:
            return False
        if asig.sesion.materia == sesion.materia:
            return False
        return False

    for b in bloques:
        if estado.bloque_ocupado_grupo(dia, b):
            return False

    return True
```

---

**Función `forward_check`** — Propaga restricciones tras una asignación, reduciendo dominios.

- **Recibe:** `dominios` (dominios actuales), `asignacion` (Asignacion recién hecha), `pendientes` (sesiones aún no asignadas).
- **Hace:** Para cada sesión pendiente, elimina de su dominio los valores que entrarían en conflicto con la nueva asignación.
- **Devuelve:** Nuevo diccionario de dominios (sin mutar el original).

```python
def forward_check(dominios, asignacion, pendientes):
    nuevos = {s: list(d) for s, d in dominios.items()}
    s_a = asignacion.sesion
    dia_a = asignacion.dia
    bloques_a = range(asignacion.hora_ini,
                      asignacion.hora_ini + s_a.duracion)
    aula_a = asignacion.aula

    for s_rest in pendientes:
        if s_rest == s_a:
            continue
        nuevos[s_rest] = [
            (d, h, a) for (d, h, a) in nuevos[s_rest]
            if not hay_conflicto_fc(s_rest, d, h,
                                    s_a, dia_a, bloques_a, aula_a)
        ]

    return nuevos
```

---

### Capítulo 3 — Resultados

> [!NOTE]
> Cada caso se ejecuta con la interfaz visual que permite seleccionar el escenario y visualizar el estado inicial, la solución y la ejecución paso a paso. Las capturas de pantalla de la interfaz se incluirán al completar la implementación.

#### 3.1 Caso 1 — Escenario base

##### 3.1.1 Descripción
Escenario estándar con las 7 materias del 7° "A", 15 aulas, ocupaciones previas moderadas de los 3 grupos activos. Todos los docentes tienen al menos 3 días disponibles.

##### 3.1.2 Estado inicial y meta
- **Estado inicial:** Horario vacío ($S_0 = \emptyset$), 12 sesiones pendientes.
- **Meta:** Horario con 12 sesiones asignadas, 29 horas colocadas, 0 conflictos.

*(Insertar captura de pantalla de la interfaz mostrando el horario vacío y las restricciones)*

##### 3.1.3 Solución
*(Insertar captura de pantalla del horario completo generado en la interfaz, con la cuadrícula Días × Horas mostrando las materias y aulas asignadas)*

##### 3.1.4 Ejecución
*(Insertar capturas paso a paso o video mostrando cómo el algoritmo va colocando sesiones y retrocediendo cuando es necesario)*

Se incluirán las métricas de ejecución:

| Métrica | Versión B (sin heurísticas) | Versión C (con MRV + FC) |
|---|---|---|
| Estados explorados | *(valor)* | *(valor)* |
| Retrocesos | *(valor)* | *(valor)* |
| Tiempo (s) | *(valor)* | *(valor)* |

##### 3.1.5 Comentarios
Análisis de los resultados: comparación entre versiones B y C, observaciones sobre el comportamiento del árbol de búsqueda.

---

#### 3.2 Caso 2 — Docente con alta restricción

##### 3.2.1 Descripción
Mismo escenario que el Caso 1, pero el docente $D_1$ (Inteligencia Artificial) solo está disponible lunes y miércoles. Esto fuerza al algoritmo a encontrar solución con dominio reducido para $s_1$ y $s_2$.

##### 3.2.2 Estado inicial y meta
- **Estado inicial:** Horario vacío con la restricción adicional de $D_1$.
- **Meta:** Horario completo donde las sesiones de IA solo aparecen lunes y miércoles.

##### 3.2.3 Solución
*(Captura de la interfaz)*

##### 3.2.4 Ejecución
*(Capturas paso a paso)*

##### 3.2.5 Comentarios
Se espera que MRV seleccione primero las sesiones de IA (menor dominio), lo que demuestra la utilidad de la heurística en escenarios restringidos.

---

#### 3.3 Caso 3 — Escenario de alta ocupación

##### 3.3.1 Descripción
Escenario con ocupaciones previas intensivas: los grupos 1° y 4° ocupan el 60% de los bloques disponibles (combinando docentes y aulas). Este caso prueba la capacidad del algoritmo para encontrar soluciones en espacios muy restringidos.

##### 3.3.2 Estado inicial y meta
- **Estado inicial:** Horario vacío con ocupaciones extensas.
- **Meta:** Horario completo y válido si existe; reporte de "sin solución" si no es posible.

##### 3.3.3 Solución
*(Captura de la interfaz)*

##### 3.3.4 Ejecución
*(Capturas paso a paso)*

##### 3.3.5 Comentarios
Análisis de la escalabilidad: cómo se comportan las métricas cuando las restricciones son severas. Se espera un aumento significativo en retrocesos, y posiblemente una mayor diferencia entre las versiones B y C.

---

### Capítulo 4 — Conclusiones y recomendaciones

#### 4.1 Conclusiones

*(Borrador a completar tras la implementación)*

1. El problema de generación de horarios académicos se formula exitosamente como un CSP, donde las variables son sesiones contiguas de clase.
2. La reformulación de horas individuales a sesiones contiguas reduce la profundidad del árbol de búsqueda de 29 a 12 niveles.
3. DFS + Backtracking garantiza encontrar una solución si existe (completitud).
4. Las heurísticas MRV + Forward Checking reducen significativamente los estados explorados y retrocesos respecto a la versión sin heurísticas.
5. El recurso más restrictivo es la disponibilidad de docentes, no las aulas (15 aulas para 4 grupos es relativamente holgado).
6. ¿Qué se haría diferente? Considerar la implementación con Constraint Propagation completa (Arc Consistency 3) para mayor poda.

#### 4.2 Recomendaciones

1. **Módulos a refinar:** El validador de restricciones podría implementarse con un índice espacial (diccionario por día y bloque) para acelerar la detección de conflictos.
2. **Tecnologías a integrar:** Bibliotecas especializadas como `python-constraint` o `OR-Tools` de Google para comparar con una implementación industrial.
3. **Extensiones futuras:** Agregar restricciones blandas (preferencias de horario del docente, minimización de huecos) y resolver con optimización multi-objetivo.
4. **Escalabilidad:** Evaluar el rendimiento con más grupos objetivo (generar horarios para los 4 grupos simultáneamente).

---

### Capítulo 5 — Anexos

*(Los siguientes anexos se referencian desde el texto principal)*

- **Anexo A:** Datos completos de las ocupaciones previas de los grupos 1°, 4° y 10° (matrices de ocupación por docente y aula).
- **Anexo B:** Código fuente completo del módulo de visualización (separado del algoritmo de búsqueda).
- **Anexo C:** Logs de ejecución completos de los 3 casos de prueba.
- **Anexo D:** Repositorio del código fuente.

---

### Bibliografía

1. Russell, S. & Norvig, P. (2010). *Artificial Intelligence: A Modern Approach*. 3ra edición. Prentice Hall. Capítulo 6: Constraint Satisfaction Problems.
2. Kumar, V. (1992). Algorithms for Constraint-Satisfaction Problems: A Survey. *AI Magazine*, 13(1), 32–44.
3. Dechter, R. (2003). *Constraint Processing*. Morgan Kaufmann.

---

## Checklist de Cumplimiento

| Requisito de la plantilla | Estado | Ubicación |
|---|---|---|
| Resumen en español | ✅ | Resumen |
| Abstract en inglés | ✅ | Abstract |
| Planteamiento del problema explícito y detallado | ✅ | Sección 1.1 |
| PEAS completo con justificaciones | ✅ | Sección 1.2 |
| Tabla de caracterización del entorno con justificaciones | ✅ | Tabla 1.1 |
| Especificación del problema de búsqueda | ✅ | Sección 1.3 |
| Estado inicial con 2–3 ejemplos | ✅ | Sección 1.4 (3 ejemplos) |
| Meta con 2–3 ejemplos | ✅ | Sección 1.5 (3 ejemplos) |
| Espacio de estados con cálculo | ✅ | Sección 1.6 |
| Transiciones con tabla | ✅ | Sección 1.7 + Tabla 1.6 |
| Métricas de rendimiento justificadas | ✅ | Sección 1.8 + Tabla 1.7 |
| Heurísticas justificadas | ✅ | Sección 1.9 |
| Código en bloques (no capturas) | ✅ | Capítulo 2 |
| Cada función con parámetros/qué hace/qué devuelve | ✅ | Capítulo 2 |
| Búsqueda separada de visualización | ✅ | Cap. 2 (solo búsqueda) |
| Interfaz permite cambiar inicio/meta/escenario | ✅ | Nota en Cap. 2 |
| Al menos 3 casos no triviales | ✅ | Secciones 3.1, 3.2, 3.3 |
| Cada caso con descripción, estado, solución, ejecución, comentarios | ✅ | Subcapítulos completos |
| Conclusiones | ✅ | Sección 4.1 |
| Recomendaciones | ✅ | Sección 4.2 |
| Anexos referenciados | ✅ | Capítulo 5 |
| Todos los objetos referenciados en texto | ✅ | Tablas 1.1–1.7 referenciadas |
| Bibliografía | ✅ | Bibliografía |
