# Horario académico sin conflictos - Generación de horarios académicos sin conflictos para grupos universitarios mediante búsqueda en profundidad con retroceso

**Integrantes:**
- Ruiz Pérez Brian Luis (Matrícula: 243738 - 7A)
- Zárate Vázquez Diego Alberto (Matrícula: 243683 - 7A)

---

## 1. Descripción del Proyecto
El proyecto consiste en diseñar un sistema de búsqueda que genere un horario académico válido para la universidad para las siete materias, respetando las restricciones curriculares, la disponibilidad de los docentes y las aulas, y los bloques horarios permitidos.

El contexto corresponde a un plan de estudios cuatrimestral de diez cuatrimestres, en el que actualmente se encuentran activos los grupos de primero, cuarto, séptimo y décimo. Los cuatrimestres regulares tienen una carga total de 525 horas, mientras que sexto y décimo corresponden a estadías de 600 horas: Estadía TSU y Estadía Profesional, respectivamente.

Debido a que la mayoría de las estadías se realizan fuera de la universidad, estas no se considerarán automáticamente como clases presenciales ni como ocupaciones de aulas. Solo se incorporarán las actividades que tengan horarios y recursos universitarios definidos.

Para mantener un alcance viable en papel y lápiz, el agente generará el horario de un grupo regular seleccionado, mientras que las ocupaciones previamente establecidas de los demás grupos se considerarán restricciones cuando compartan docentes o aulas. Se utilizará búsqueda en profundidad con retroceso (Depth-First Search con Backtracking), que probará asignaciones de materias, rechazará las que generen conflictos y retrocederá cuando sea necesario.

---

## 2. Formulación PEAS

### P – Performance (Medida de Desempeño)
Generar un horario completo y válido para las siete materias del grupo seleccionado, sin conflictos de horario, respetando la disponibilidad de docentes y aulas, las restricciones curriculares y los horarios fijos contemplados en el escenario.

Como criterios secundarios, se buscará reducir el número de estados explorados y la cantidad de retrocesos necesarios para encontrar una solución.

### E – Environment (Entorno)
Modelo estático y discreto de una universidad, compuesto por un grupo regular con siete materias, bloques horarios disponibles, docentes, aulas, restricciones de asignación y ocupaciones previamente establecidas de los demás grupos activos.

El plan de estudios contempla diez cuatrimestres. Los cuatrimestres regulares tienen una carga total de 525 horas, mientras que sexto y décimo corresponden a estadías de 600 horas cada una. La carga horaria se considerará una restricción curricular; su distribución concreta en bloques requerirá los datos correspondientes a las materias y al calendario académico.

Se asume que toda la información utilizada está definida antes de comenzar la búsqueda y que no cambia durante su ejecución.

### A – Actuadores
- Asignar una materia pendiente a un bloque horario y un aula disponibles.
- Aceptar una asignación cuando cumple todas las restricciones.
- Rechazar una asignación que genera conflictos.
- Deshacer una asignación y probar otra alternativa mediante retroceso.
- Incorporar la asignación válida al horario parcial hasta completar el horario.

### S – Sensores
- Lista de las siete materias que deben programarse.
- Docentes responsables y sus disponibilidades.
- Aulas disponibles, capacidades y restricciones de uso.
- Bloques horarios permitidos.
- Asignaciones previamente establecidas de otros grupos.
- Carga horaria y requisitos curriculares de las materias.
- Estado actual del horario parcial y conflictos detectados.

---

## 3. Características del Entorno
- **Determinista:** Sí
- **Monoagente:** Sí
- **Secuencial:** Sí
- **Observable:** Sí
- **Discreto:** Sí
- **Estático:** Sí
- **Conocido:** Sí

---

## 4. Transiciones
- **INICIO:** Horario del grupo seleccionado sin nuevas asignaciones, con las siete materias pendientes y con las restricciones de docentes, aulas, disponibilidad y ocupaciones ya conocidas.
- $\rightarrow$ Seleccionar una materia pendiente.
- $\rightarrow$ Asignarla a un bloque horario y aula disponibles.
- $\rightarrow$ Comprobar que no existan conflictos con el grupo, el docente, el aula ni las restricciones curriculares.
- $\rightarrow$ Si la asignación es válida, conservarla y continuar con la siguiente materia.
- $\rightarrow$ Si la asignación es inválida o impide completar el horario, deshacerla y probar una alternativa.
- $\rightarrow$ Repetir el proceso hasta completar todas las materias.
- **FINAL:** Horario completo con las siete materias asignadas, sin conflictos y respetando las restricciones definidas.

---

## 5. Espacio de Estados
Cada estado representa un horario parcial del grupo seleccionado. Se define como un conjunto de asignaciones:

$$S = \{ (\text{materia}, \text{bloque\_horario}, \text{aula}) \}$$

Un estado puede contener desde cero hasta siete materias asignadas. Cada transición agrega una asignación válida o, cuando se detecta un conflicto, deshace una asignación para probar otra alternativa. 

- **Estado inicial:** Es el horario sin asignaciones nuevas para el grupo seleccionado, junto con las restricciones y ocupaciones previamente establecidas.
- **Estado objetivo:** Es un horario completo en el que las siete materias están asignadas y se cumplen todas las restricciones.

---

## 6. Rendimiento (Métricas de Evaluación)
1. **Validez del horario:** Cumplimiento de todas las restricciones establecidas.
2. **Número de materias asignadas:** Cantidad de materias colocadas correctamente, con un objetivo de siete.
3. **Número de conflictos finales:** Cantidad de solapamientos o restricciones incumplidas; el objetivo es cero.
4. **Estados explorados:** Cantidad de estados examinados durante la búsqueda.
5. **Número de retrocesos:** Cantidad de asignaciones deshechas para probar alternativas.
6. **Tiempo de resolución:** Tiempo necesario para completar la búsqueda y encontrar una solución válida.

---

## 7. Heurística
**No aplica.** El proyecto utilizará búsqueda en profundidad con retroceso (DFS + Backtracking), un método de búsqueda no informada que no emplea una función heurística ($h(n)$) para estimar la distancia o el costo restante hasta la solución. 

Las restricciones de disponibilidad de docentes, aulas y horarios se utilizarán para validar las asignaciones y descartar las que generen conflictos, no como una estimación heurística de la solución.