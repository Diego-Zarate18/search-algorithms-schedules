# Horario académico sin conflictos - Generación de horarios académicos sin conflictos para grupos universitarios mediante búsqueda en profundidad con retroceso

**Integrantes:**
- Ruiz Pérez Brian Luis (Matrícula: 243738 - 7A)
- Zárate Vázquez Diego Alberto (Matrícula: 243683 - 7A)

> **Nota de versión:** este documento conserva la propuesta registrada e incorpora las precisiones acordadas para su implementación (modelado por sesiones, jornada de 8:00 a 16:00, aula fija y exclusiones de alcance). La versión original registrada se conserva en el historial del repositorio.

---

## 1. Descripción del Proyecto
El proyecto consiste en diseñar un sistema de búsqueda que genere un horario académico válido para las siete materias de un grupo universitario, respetando las restricciones curriculares, la disponibilidad de los docentes y del aula, y los bloques horarios permitidos.

El contexto corresponde al plan de estudios cuatrimestral de diez cuatrimestres de la Ingeniería en Tecnologías de la Información e Innovación Digital, en el que actualmente se encuentran activos los grupos de primero, cuarto, séptimo y décimo. Los cuatrimestres regulares tienen una carga total de 525 horas (35 horas semanales durante 15 semanas), mientras que sexto y décimo corresponden a estadías de 600 horas: Estadía TSU y Estadía Profesional, respectivamente.

Debido a que las estadías se realizan principalmente fuera de la universidad y solo cuentan con un seguimiento por tutoría de pocas horas, no se consideran clases presenciales ni ocupaciones de docentes o aulas.

Para mantener un alcance viable, el agente genera el horario de un único grupo regular (7° "A"), mientras que las ocupaciones previamente establecidas de los demás grupos se consideran restricciones cuando comparten docentes. Cada materia se divide en sesiones de dos horas, y se utiliza búsqueda en profundidad con retroceso (Depth-First Search con Backtracking), que prueba asignaciones de sesiones, rechaza las que generan conflictos y retrocede cuando es necesario.

---

## 2. Alcance y Supuestos
- **Grupo programado:** 7° "A", con siete materias y 35 horas semanales.
- **Jornada:** lunes a viernes, de 8:00 a 16:00, dividida en 4 bloques de 2 horas por día (20 bloques semanales).
- **Sesiones:** cada materia se divide en sesiones de 2 horas. Inglés VI (5 h) se divide en dos sesiones de 2 h y una de 1 h; la sesión de 1 h ocupa un bloque completo y la hora restante queda libre para el grupo. En total se programan 18 sesiones.
- **Aula:** el grupo cuenta con un aula fija asignada (Aula 7A); todas sus sesiones se imparten en ella.
- **Otros grupos (1°, 4°, 7° "B" y 7° "C"):** no se programan; sus horarios ya establecidos se representan como bloques ocupados de los docentes compartidos.
- **Estadías (6° y 10°):** documentadas en el contexto, pero excluidas del modelo.
- **Tutoría grupal:** excluida, ya que no forma parte de la carga curricular del plan de estudios. Puede ubicarse posteriormente en las horas libres del horario generado.

---

## 3. Formulación PEAS

### P – Performance (Medida de Desempeño)
Generar un horario completo y válido para las siete materias del grupo seleccionado (18 sesiones), sin conflictos de horario, respetando la disponibilidad de los docentes y del aula, las restricciones curriculares y las ocupaciones fijas de los demás grupos.

Como criterios secundarios, se registran el número de estados explorados y la cantidad de retrocesos necesarios para encontrar una solución.

### E – Environment (Entorno)
Modelo estático y discreto de una universidad, compuesto por un grupo regular con siete materias divididas en sesiones, 20 bloques horarios semanales, siete docentes, un aula asignada, restricciones de asignación y ocupaciones previamente establecidas de los demás grupos activos.

La carga horaria semanal de cada materia se considera una restricción curricular: determina cuántas sesiones deben programarse para ella.

Se asume que toda la información utilizada está definida antes de comenzar la búsqueda y que no cambia durante su ejecución.

### A – Actuadores
- Asignar una sesión pendiente a un bloque horario y al aula del grupo.
- Aceptar una asignación cuando cumple todas las restricciones.
- Rechazar una asignación que genera conflictos.
- Deshacer una asignación y probar otra alternativa mediante retroceso.
- Incorporar la asignación válida al horario parcial hasta completar el horario.

### S – Sensores
- Lista de las siete materias y de las sesiones que deben programarse.
- Docente responsable de cada materia y sus bloques ocupados con otros grupos.
- Aula asignada al grupo y su disponibilidad.
- Bloques horarios permitidos.
- Carga horaria de cada materia.
- Estado actual del horario parcial y conflictos detectados.

---

## 4. Características del Entorno
- **Determinista:** Sí
- **Monoagente:** Sí
- **Secuencial:** Sí
- **Observable:** Sí (totalmente)
- **Discreto:** Sí
- **Estático:** Sí
- **Conocido:** Sí

---

## 5. Transiciones
- **INICIO:** horario del grupo sin asignaciones, con las 18 sesiones pendientes y con las ocupaciones de los docentes ya conocidas.
- $\rightarrow$ Seleccionar la siguiente sesión pendiente (en un orden fijo).
- $\rightarrow$ Asignarla a un bloque horario en el aula del grupo.
- $\rightarrow$ Comprobar que no existan conflictos con el grupo, el docente, el aula ni las restricciones curriculares.
- $\rightarrow$ Si la asignación es válida, conservarla y continuar con la siguiente sesión.
- $\rightarrow$ Si la asignación es inválida, probar el siguiente bloque; si ningún bloque es válido, retroceder, deshacer la asignación anterior y probar otra alternativa.
- $\rightarrow$ Repetir el proceso hasta completar todas las sesiones.
- **FINAL:** horario completo con las siete materias (18 sesiones) asignadas, sin conflictos y respetando las restricciones definidas.

---

## 6. Espacio de Estados
Cada estado representa un horario parcial del grupo seleccionado. Se define como un conjunto de asignaciones:

$$S = \{ (\text{sesión}, \text{bloque\_horario}, \text{aula}) \}$$

donde cada sesión pertenece a una materia (por ejemplo, la sesión 2 de Fundamentos de Inteligencia Artificial). Un estado puede contener desde cero hasta 18 sesiones asignadas; una materia se considera asignada cuando todas sus sesiones han sido colocadas. Cada transición agrega una asignación válida o, cuando se detecta que no existe alternativa, deshace una asignación para probar otra.

- **Estado inicial:** horario sin asignaciones para el grupo, junto con las restricciones y ocupaciones previamente establecidas.
- **Estado objetivo:** horario completo en el que las 18 sesiones de las siete materias están asignadas y se cumplen todas las restricciones.

### Restricciones
1. **Grupo:** el grupo no puede tener dos sesiones en el mismo bloque.
2. **Docente:** el docente de la materia no puede estar ocupado con otro grupo en ese bloque.
3. **Distribución:** una materia no puede tener más de una sesión por día (máximo 2 horas diarias por materia).
4. **Orden de sesiones:** las sesiones equivalentes de una misma materia se colocan en días estrictamente crecientes, para no explorar varias veces el mismo horario.

---

## 7. Rendimiento (Métricas de Evaluación)
1. **Validez del horario:** cumplimiento de todas las restricciones establecidas.
2. **Número de materias asignadas:** cantidad de materias con todas sus sesiones colocadas, con un objetivo de siete (18 sesiones).
3. **Número de conflictos finales:** cantidad de solapamientos o restricciones incumplidas; el objetivo es cero.
4. **Estados explorados:** cantidad de asignaciones candidatas evaluadas durante la búsqueda.
5. **Número de retrocesos:** cantidad de asignaciones deshechas para probar alternativas.
6. **Tiempo de resolución:** tiempo de cómputo necesario para completar la búsqueda y encontrar una solución válida.

---

## 8. Heurística
**No aplica.** El proyecto utiliza búsqueda en profundidad con retroceso (DFS + Backtracking), un método de búsqueda no informada que no emplea una función heurística ($h(n)$) para estimar la distancia o el costo restante hasta la solución.

Las sesiones y los bloques se recorren en un orden fijo definido de antemano. Las restricciones se utilizan únicamente para validar las asignaciones y descartar las que generan conflictos, no como una estimación heurística de la solución. Técnicas como elegir primero la sesión con menos bloques disponibles (MRV) se consideran búsqueda informada y quedan fuera del alcance.
