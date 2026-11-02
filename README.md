# Horario académico sin conflictos

Generación del horario semanal de un grupo universitario (7° A, Ingeniería en Tecnologías de la Información e Innovación Digital) mediante **búsqueda en profundidad con retroceso (DFS + Backtracking)**, un método de búsqueda no informada.

Proyecto de la materia Fundamentos de Inteligencia Artificial (U2).
**Integrantes:** Ruiz Pérez Brian Luis (243738) · Zárate Vázquez Diego Alberto (243683)

## El problema en breve

- 7 materias (35 h/semana) divididas en **18 sesiones** de 2 h (Inglés: 2 + 2 + 1).
- Jornada de lunes a viernes, 8:00–16:00, en **20 bloques** de 2 h.
- Los demás grupos no se programan; sus clases ya fijas aparecen como bloques ocupados de los docentes.
- Restricciones:
  1. **R1 Grupo:** el grupo no tiene dos sesiones en el mismo bloque.
  2. **R2 Docente:** el docente no está ocupado con otro grupo en ese bloque.
  3. **R3 Distribución:** una materia tiene como máximo una sesión por día.
  4. **R4 Orden:** las sesiones equivalentes de una materia van en días crecientes.

Detalle completo en [`docs/propuesta_registrada.md`](docs/propuesta_registrada.md) y [`docs/decisiones_tecnicas.md`](docs/decisiones_tecnicas.md).

## Requisitos

- Python 3.10 o superior (en Windows, el instalador oficial ya incluye Tkinter).
- Dependencias: `pip install -r requirements.txt`

## Uso

Todos los comandos se ejecutan **desde la raíz del proyecto** (el código es el paquete `src`):

```bash
python -m src.main              # abre la interfaz (elegir caso → Ejecutar búsqueda → reproducir)
python -m src.espacio_estados   # tamaño del espacio de estados por niveles
python -m src.resultados        # resumen de los casos en salidas/resultados/
python -m src.graficas          # gráficas de los casos en salidas/graficas/
python -m unittest -v           # ejecuta las pruebas
```

En la interfaz: **Espacio** reproduce o pausa, **←/→** avanzan un paso, **Inicio** reinicia y **Fin** va al final. Si el intérprete no tiene Tkinter, `src.main` explica cómo instalarlo.

## Estructura

```
├── docs/                 propuesta, decisiones técnicas, borrador y referencias (PDF)
├── src/
│   ├── main.py           punto de entrada
│   ├── modelo.py         entidades: Materia, Sesion, BloqueHorario, Asignacion, EstadoHorario, Escenario
│   ├── escenarios.py     datos de los 4 casos y de los 2 escenarios mini
│   ├── restricciones.py  reglas R1–R4 con motivo de rechazo
│   ├── busqueda.py       agente DFS + eventos para la interfaz
│   ├── metricas.py       estados explorados, retrocesos por nivel y tiempo
│   ├── verificacion.py   verificación final independiente
│   ├── reproduccion.py   recorrido paso a paso de la traza de eventos (sin Tkinter)
│   ├── interfaz.py       interfaz Tkinter que reproduce la búsqueda paso a paso
│   ├── espacio_estados.py  tamaño del espacio de estados por niveles
│   ├── resultados.py     resumen por caso (métricas, horarios válidos y horario final)
│   └── graficas.py       gráficas de retrocesos por nivel y comparación de casos (PNG)
├── tests/                pruebas unitarias
└── salidas/              gráficas y resultados generados (no se versionan)
```

## Estado

| Componente | Estado |
|---|---|
| Modelo y escenario base | listo |
| Restricciones (R1–R4) y agente DFS con eventos | listo (reproduce el caso 1) |
| Verificación final independiente | listo |
| Casos 2–4 y escenarios mini | listo |
| Interfaz Tkinter con reproducción paso a paso | listo |
| Espacio de estados y resumen de resultados | listo |
| Gráficas de resultados | listo |
