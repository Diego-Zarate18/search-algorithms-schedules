# Documento de Decisiones Técnicas e Implementación

**Proyecto:** Generación de horarios académicos sin conflictos mediante DFS + Backtracking  
**Materia:** Inteligencia Artificial  
**Autores:** Ruiz Pérez Brian Luis & Zárate Vázquez Diego Alberto  

---

## 1. Arquitectura Técnica y Lenguaje
- **Lenguaje:** Python 3.10+
- **Paradigma:** Orientado a Objetos (POO) estructurado modularmente para facilitar la inspección del árbol de búsqueda.
- **Librerías recomendadas:**
  - `matplotlib` / `seaborn`: Para la generación gráfica de métricas (número de retrocesos por nivel de profundidad, comparación de estados explorados vs. solución).
  - `pandas` (Opcional): Para la representación matricial y exportación limpia del horario académico final en formato de tabla (Días vs. Horas).

---

## 2. Definición Concreta del Dominio de Datos

Para ejecutar el algoritmo de búsqueda de forma controlada y determinista, se establece el siguiente escenario de pruebas:

1. **Grupo Objetivos:** $G_{\text{target}} = \text{7° "A"}$ (Ingeniería en Desarrollo de Software).
2. **Materias Pendientes ($M_1$ a $M_7$):**
   - $M_1$: Inteligencia Artificial (Docente: $D_1$, Carga: 5 hrs/semana)
   - $M_2$: Bases de Datos en la Nube (Docente: $D_2$, Carga: 5 hrs/semana)
   - $M_3$: Seguridad Informática (Docente: $D_3$, Carga: 4 hrs/semana)
   - $M_4$: Ética y legislación (Docente: $D_4$, Carga: 4 hrs/semana)
   - $M_5$: Formulación de Proyectos (Docente: $D_5$, Carga: 5 hrs/semana)
   - $M_6$: Inglés VI (Docente: $D_6$, Carga: 3 hrs/semana)
   - $M_7$: Habilidades Gerenciales (Docente: $D_7$, Carga: 3 hrs/semana)
3. **Bloques Horarios ($T$):**
   - Días: Lunes a Viernes.
   - Bloques por día: 7 bloques de 1 hora (07:00 - 08:00, 08:00 - 09:00, ..., 13:00 - 14:00).
   - Total de bloques semanales disponibles: $5 \times 7 = 35$ bloques.
4. **Matriz de Ocupaciones Previas (Restricciones del Entorno):**
   - Ocupaciones fijeza de docentes $D_1 \dots D_7$ atendiendo a otros grupos activos (1°, 4°, 10°) en bloques específicos.

---

## 3. Algoritmo de Búsqueda: DFS + Backtracking

### Pseudo-código de la Función Principal Recursiva

```python
def dfs_backtracking(estado_actual, materias_pendientes):
    # Caso Base: Todas las materias asignadas sin conflicto
    if len(materias_pendientes) == 0:
        return estado_actual  # Estado Objetivo alcanzado

    materia_actual = materias_pendientes[0]

    for bloque in obtener_bloques_disponibles():
        for aula in obtener_aulas_disponibles():
            # Incrementar contador de estados explorados
            contador_estados_explorados += 1
            
            # Validar restricciones hard
            if es_asignacion_valida(materia_actual, bloque, aula, estado_actual):
                # Aplicar transición (Actuador: Asignar)
                nueva_asignacion = (materia_actual, bloque, aula)
                estado_actual.agregar(nueva_asignacion)
                
                # Llamada recursiva en profundidad
                resultado = dfs_backtracking(estado_actual, materias_pendientes[1:])
                if resultado es no Nulo:
                    return resultado
                
                # Backtracking (Actuador: Deshacer asignación)
                contador_retrocesos += 1
                estado_actual.remover(nueva_asignacion)

    return None  # Fallo en esta rama
```

---

## 4. Estructura del Entregable Final (Reporte Técnico)

El reporte final mantendrá la estructura estándar de evaluación universitaria (basado en el reporte de referencia de la institución):

1. **Portada Institucional:**
   - Materia, Corte, Integrantes, Matrícula y Fecha.
2. **Introducción:**
   - Marco conceptual de CSP (Problemas de Satisfacción de Restricciones) y formulación mediante espacios de estados.
3. **Especificación del Sistema y Agente:**
   - Tabla PEAS detallada.
   - Tabla de características del entorno.
4. **Diseño e Implementación:**
   - Estructura de clases en Python (`AgenteDFS`, `EstadoHorario`, `ValidadorRestricciones`).
   - Explicación del mecanismo de pila recursiva y pruning/poda de conflictos.
5. **Resultados y Tablas de Rendimiento:**
   - Matriz visual del horario generado para el 7° "A".
   - Reporte de las 6 métricas de rendimiento registradas (Validez, Materias Asignadas, Conflictos, Estados Explorados, Retrocesos, Tiempo de Cómputo).
   - Gráfica de evolución de retrocesos por nivel de árbol.
6. **Discusión y Conclusión:**
   - Análisis de la eficiencia de la poda en DFS vs. la complejidad del espacio combinatorio.
7. **Bibliografía.**