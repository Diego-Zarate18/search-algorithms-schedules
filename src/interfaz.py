"""Interfaz gráfica (Tkinter) que reproduce la búsqueda paso a paso.

Flujo: se elige un caso (se muestran sus datos y la cuadrícula vacía),
se ejecuta la búsqueda (instantánea) y después se reproduce su traza con
los controles. La búsqueda nunca corre dentro del ciclo de eventos: la
interfaz solo recorre la lista de eventos con ``after()``.
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import Callable

from .busqueda import AgenteDFS, TipoEvento
from .escenarios import ESCENARIOS, ESCENARIOS_MINI
from .modelo import Escenario
from .reproduccion import Reproductor, describir
from .verificacion import verificar

# Paleta "Analytics Dashboard": azul para datos, ámbar para resaltar.
COLOR = {
    "fondo": "#F8FAFC",
    "tarjeta": "#FFFFFF",
    "borde": "#E2E8F0",
    "texto": "#0F172A",
    "texto_suave": "#475569",
    "primario": "#1E40AF",
    "primario_activo": "#1E3A8A",
    "acento": "#B45309",
    "exito": "#15803D",
    "error": "#DC2626",
    "retroceso": "#6D28D9",
    "deshabilitado": "#94A3B8",
}

# Relleno por materia (tonos claros con texto oscuro: contraste > 7:1).
COLOR_MATERIA = (
    "#DBEAFE",
    "#D1FAE5",
    "#FEF3C7",
    "#EDE9FE",
    "#FFE4E6",
    "#CFFAFE",
    "#ECFCCB",
)

# El estado del paso se indica con texto además del color.
ESTADO_FOCO = {
    TipoEvento.PROBAR: ("PROBANDO", COLOR["acento"]),
    TipoEvento.ACEPTAR: ("ACEPTADA", COLOR["exito"]),
    TipoEvento.RECHAZAR: ("RECHAZO", COLOR["error"]),
    TipoEvento.RETROCEDER: ("RETROCESO", COLOR["retroceso"]),
}

VELOCIDAD_MIN, VELOCIDAD_MAX = 1, 2000  # pasos por segundo

# Casos del selector: los cuatro de resultados y los dos mini de trazas manuales.
CASOS = {**ESCENARIOS, **ESCENARIOS_MINI}


def _elegir_fuente(preferidas: tuple[str, ...], respaldo: str) -> str:
    disponibles = set(tkfont.families())
    return next((f for f in preferidas if f in disponibles), respaldo)


class CeldaHorario(tk.Frame):
    """Celda: sesión asignada, estado del paso actual y docentes ocupados."""

    ANCHO, ALTO = 124, 112

    def __init__(
        self, padre: tk.Widget, fuentes: dict[str, tuple], ocupados: str
    ) -> None:
        super().__init__(
            padre,
            width=self.ANCHO,
            height=self.ALTO,
            bg=COLOR["tarjeta"],
            highlightthickness=3,
            highlightbackground=COLOR["borde"],
        )
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)

        self.estado = tk.Label(self, font=fuentes["etiqueta"], anchor="w", padx=6)
        self.sesion = tk.Label(self, font=fuentes["dato_grande"], anchor="w", padx=6)
        self.nombre = tk.Label(
            self,
            font=fuentes["mini"],
            anchor="nw",
            justify="left",
            wraplength=self.ANCHO - 16,
            padx=6,
        )
        self.ocupados = tk.Label(
            self,
            text=ocupados,
            font=fuentes["mini"],
            anchor="w",
            padx=6,
            justify="left",
            wraplength=self.ANCHO - 16,
            fg=COLOR["texto_suave"],
        )
        self.estado.grid(row=0, column=0, sticky="ew")
        self.sesion.grid(row=1, column=0, sticky="ew")
        self.nombre.grid(row=2, column=0, sticky="nsew")
        self.ocupados.grid(row=3, column=0, sticky="sew", pady=(0, 2))
        self.rowconfigure(2, weight=1)

    def mostrar(
        self, sesion_id: str, nombre: str, relleno: str, estado: tuple[str, str] | None
    ) -> None:
        self.configure(
            bg=relleno, highlightbackground=estado[1] if estado else COLOR["borde"]
        )
        for etiqueta in (self.sesion, self.nombre, self.ocupados):
            etiqueta.configure(bg=relleno)
        self.sesion.configure(text=sesion_id, fg=COLOR["texto"])
        self.nombre.configure(text=nombre, fg=COLOR["texto"])
        if estado:
            self.estado.configure(text=estado[0], bg=estado[1], fg="#FFFFFF")
        else:
            self.estado.configure(text="", bg=relleno)


class Aplicacion(ttk.Frame):
    """Ventana principal."""

    def __init__(
        self, raiz: tk.Tk, escenarios: dict[str, Callable[[], Escenario]] = CASOS
    ) -> None:
        super().__init__(raiz, style="Fondo.TFrame", padding=12)
        self.raiz = raiz
        self.escenarios = escenarios
        self.escenario: Escenario | None = None
        self.reproductor: Reproductor | None = None
        self._tarea: str | None = None
        self.reproduciendo = False

        self._configurar_estilos()
        self._construir()
        self._atajos()
        self.grid(row=0, column=0, sticky="nsew")
        raiz.rowconfigure(0, weight=1)
        raiz.columnconfigure(0, weight=1)

        self.combo_caso.current(0)
        self.seleccionar_escenario()

    # Construcción -----------------------------------------------------

    def _configurar_estilos(self) -> None:
        sans = _elegir_fuente(
            ("Segoe UI", "Helvetica Neue", "DejaVu Sans"), "TkDefaultFont"
        )
        mono = _elegir_fuente(
            ("Consolas", "Cascadia Mono", "DejaVu Sans Mono"), "TkFixedFont"
        )
        self.fuentes = {
            "titulo": (sans, 15, "bold"),
            "subtitulo": (sans, 10),
            "seccion": (sans, 11, "bold"),
            "normal": (sans, 10),
            "pequena": (sans, 9),
            "mini": (sans, 8),
            "etiqueta": (sans, 8, "bold"),
            "dato": (mono, 10),
            "dato_grande": (mono, 11, "bold"),
            "bitacora": (mono, 9),
        }
        self.raiz.configure(bg=COLOR["fondo"])
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        estilo.configure(
            ".",
            font=self.fuentes["normal"],
            background=COLOR["fondo"],
            foreground=COLOR["texto"],
        )
        estilo.configure("Fondo.TFrame", background=COLOR["fondo"])
        estilo.configure(
            "Tarjeta.TFrame",
            background=COLOR["tarjeta"],
            relief="solid",
            borderwidth=1,
            bordercolor=COLOR["borde"],
        )
        estilo.configure("Interior.TFrame", background=COLOR["tarjeta"])
        estilo.configure("Tarjeta.TLabel", background=COLOR["tarjeta"])
        estilo.configure(
            "Seccion.TLabel", background=COLOR["tarjeta"], font=self.fuentes["seccion"]
        )
        estilo.configure(
            "Suave.TLabel",
            background=COLOR["tarjeta"],
            foreground=COLOR["texto_suave"],
            font=self.fuentes["pequena"],
        )
        estilo.configure(
            "Dato.TLabel", background=COLOR["tarjeta"], font=self.fuentes["dato"]
        )
        estilo.configure("Titulo.TLabel", font=self.fuentes["titulo"])
        estilo.configure(
            "Subtitulo.TLabel",
            foreground=COLOR["texto_suave"],
            font=self.fuentes["subtitulo"],
        )
        estilo.configure(
            "TButton",
            padding=(10, 6),
            background=COLOR["tarjeta"],
            bordercolor=COLOR["borde"],
        )
        estilo.map(
            "TButton",
            background=[("active", COLOR["borde"])],
            foreground=[("disabled", COLOR["deshabilitado"])],
        )
        estilo.configure(
            "Primario.TButton",
            background=COLOR["primario"],
            foreground="#FFFFFF",
            bordercolor=COLOR["primario"],
            font=(sans, 10, "bold"),
        )
        estilo.map(
            "Primario.TButton",
            background=[
                ("disabled", COLOR["borde"]),
                ("active", COLOR["primario_activo"]),
            ],
            foreground=[("disabled", COLOR["deshabilitado"])],
        )
        estilo.map(
            "TCombobox",
            fieldbackground=[("readonly", COLOR["tarjeta"])],
            selectbackground=[("readonly", COLOR["tarjeta"])],
            selectforeground=[("readonly", COLOR["texto"])],
        )
        estilo.configure(
            "Encabezado.TLabel",
            background=COLOR["tarjeta"],
            foreground=COLOR["texto_suave"],
            font=(sans, 8, "bold"),
        )
        estilo.configure("Tarjeta.Horizontal.TScale", background=COLOR["tarjeta"])
        estilo.configure(
            "Horizontal.TProgressbar",
            background=COLOR["primario"],
            troughcolor=COLOR["borde"],
            bordercolor=COLOR["borde"],
        )

    def _construir(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self._construir_encabezado().grid(
            row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10)
        )
        self._construir_datos().grid(row=1, column=0, sticky="nsw", padx=(0, 10))
        self._construir_horario().grid(row=1, column=1, sticky="nsew")
        self._construir_progreso().grid(row=1, column=2, sticky="nse", padx=(10, 0))
        self._construir_controles().grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0)
        )

    def _tarjeta(self, titulo: str) -> ttk.Frame:
        marco = ttk.Frame(self, style="Tarjeta.TFrame", padding=12)
        ttk.Label(marco, text=titulo, style="Seccion.TLabel").pack(
            anchor="w", pady=(0, 6)
        )
        return marco

    def _construir_encabezado(self) -> ttk.Frame:
        marco = ttk.Frame(self, style="Fondo.TFrame")
        marco.columnconfigure(0, weight=1)
        ttk.Label(
            marco, text="Horario académico sin conflictos", style="Titulo.TLabel"
        ).grid(row=0, column=0, sticky="w")
        self.subtitulo = ttk.Label(marco, style="Subtitulo.TLabel")
        self.subtitulo.grid(row=1, column=0, sticky="w")

        selector = ttk.Frame(marco, style="Fondo.TFrame")
        selector.grid(row=0, column=1, rowspan=2, sticky="e")
        ttk.Label(selector, text="Caso").pack(side="left", padx=(0, 6))
        self.claves = list(self.escenarios)
        self.combo_caso = ttk.Combobox(
            selector,
            state="readonly",
            width=34,
            values=[crear().nombre for crear in self.escenarios.values()],
        )
        self.combo_caso.bind(
            "<<ComboboxSelected>>", lambda _e: self.seleccionar_escenario()
        )
        self.combo_caso.pack(side="left", padx=(0, 8))
        self.boton_ejecutar = ttk.Button(
            selector,
            text="Ejecutar búsqueda",
            style="Primario.TButton",
            command=self.ejecutar,
        )
        self.boton_ejecutar.pack(side="left")

        self.descripcion = ttk.Label(marco, style="Subtitulo.TLabel", wraplength=1000)
        self.descripcion.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
        return marco

    def _construir_datos(self) -> ttk.Frame:
        marco = self._tarjeta("Datos de entrada")
        ttk.Label(
            marco, text="Materias, en el orden fijo de búsqueda", style="Suave.TLabel"
        ).pack(anchor="w")
        self.tabla_materias = ttk.Frame(marco, style="Interior.TFrame")
        self.tabla_materias.pack(anchor="w", fill="x", pady=(4, 12))
        ttk.Label(
            marco,
            text="Ocupaciones de los docentes con otros grupos",
            style="Suave.TLabel",
        ).pack(anchor="w")
        self.tabla_ocupaciones = ttk.Frame(marco, style="Interior.TFrame")
        self.tabla_ocupaciones.pack(anchor="w", fill="x", pady=(4, 0))
        return marco

    def _tabla(
        self,
        marco: ttk.Frame,
        encabezados: tuple[str, ...],
        filas: list[tuple[str, ...]],
        anchos: tuple[int, ...],
    ) -> None:
        """Tabla simple de etiquetas; la última columna envuelve el texto largo."""
        for hijo in marco.winfo_children():
            hijo.destroy()
        for c, texto in enumerate(encabezados):
            ttk.Label(marco, text=texto, style="Encabezado.TLabel").grid(
                row=0, column=c, sticky="w", padx=(0, 8), pady=(0, 2)
            )
        for f, fila in enumerate(filas, start=1):
            for c, texto in enumerate(fila):
                es_dato = c == 0 or encabezados[c] in ("Doc.", "Total")
                ttk.Label(
                    marco,
                    text=texto,
                    wraplength=anchos[c],
                    justify="left",
                    style="Dato.TLabel" if es_dato else "Tarjeta.TLabel",
                    font=self.fuentes["pequena"] if not es_dato else None,
                ).grid(row=f, column=c, sticky="nw", padx=(0, 8), pady=1)

    def _construir_horario(self) -> ttk.Frame:
        marco = self._tarjeta("Horario del grupo")
        rejilla = tk.Frame(marco, bg=COLOR["tarjeta"])
        rejilla.pack(anchor="n")
        self.rejilla = rejilla
        self.celdas: dict[str, CeldaHorario] = {}

        leyenda = ttk.Frame(marco, style="Interior.TFrame")
        leyenda.pack(side="bottom", anchor="w", pady=(10, 0))
        for texto, color in ESTADO_FOCO.values():
            tk.Label(
                leyenda,
                text=f" {texto} ",
                bg=color,
                fg="#FFFFFF",
                font=self.fuentes["etiqueta"],
            ).pack(side="left", padx=(0, 6))
        ttk.Label(
            leyenda,
            text="Ocup.: docentes ocupados con otros grupos",
            style="Suave.TLabel",
        ).pack(side="left", padx=(4, 0))
        return marco

    def _construir_progreso(self) -> ttk.Frame:
        marco = self._tarjeta("Progreso de la búsqueda")
        self.etiqueta_paso = ttk.Label(marco, style="Dato.TLabel")
        self.etiqueta_paso.pack(anchor="w")
        self.barra = ttk.Progressbar(marco, length=230, mode="determinate")
        self.barra.pack(anchor="w", pady=(4, 10))

        metricas = ttk.Frame(marco, style="Interior.TFrame")
        metricas.pack(anchor="w", fill="x")
        self.valores: dict[str, ttk.Label] = {}
        for fila, (clave, texto) in enumerate(
            (
                ("explorados", "Estados explorados"),
                ("retrocesos", "Retrocesos"),
                ("colocadas", "Sesiones colocadas"),
                ("nivel", "Nivel actual (sesión)"),
            )
        ):
            ttk.Label(metricas, text=texto, style="Tarjeta.TLabel").grid(
                row=fila, column=0, sticky="w"
            )
            self.valores[clave] = ttk.Label(
                metricas, style="Dato.TLabel", anchor="e", width=11
            )
            self.valores[clave].grid(row=fila, column=1, sticky="e", padx=(12, 0))

        ttk.Label(marco, text="Último paso", style="Seccion.TLabel").pack(
            anchor="w", pady=(12, 2)
        )
        self.ultimo_paso = ttk.Label(
            marco, style="Tarjeta.TLabel", wraplength=230, justify="left"
        )
        self.ultimo_paso.pack(anchor="w", fill="x")

        ttk.Label(marco, text="Bitácora", style="Seccion.TLabel").pack(
            anchor="w", pady=(12, 2)
        )
        self.bitacora = tk.Listbox(
            marco,
            height=10,
            width=30,
            font=self.fuentes["bitacora"],
            activestyle="none",
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLOR["borde"],
            selectbackground=COLOR["tarjeta"],
            selectforeground=COLOR["texto"],
        )
        self.bitacora.pack(anchor="w", fill="x")

        ttk.Label(marco, text="Verificación final", style="Seccion.TLabel").pack(
            anchor="w", pady=(12, 2)
        )
        self.verificacion = tk.Label(
            marco,
            font=self.fuentes["normal"],
            anchor="w",
            justify="left",
            bg=COLOR["tarjeta"],
            padx=8,
            pady=6,
        )
        self.verificacion.pack(anchor="w", fill="x")
        return marco

    def _construir_controles(self) -> ttk.Frame:
        marco = ttk.Frame(self, style="Tarjeta.TFrame", padding=10)
        botones = (
            ("reiniciar", "Reiniciar [Inicio]", self.reiniciar),
            ("anterior", "Paso anterior [←]", self.paso_anterior),
            ("reproducir", "Reproducir [Espacio]", self.alternar_reproduccion),
            ("siguiente", "Paso siguiente [→]", self.paso_siguiente),
            ("final", "Ir al final [Fin]", self.ir_al_final),
        )
        self.botones: dict[str, ttk.Button] = {}
        for clave, texto, accion in botones:
            estilo = "Primario.TButton" if clave == "reproducir" else "TButton"
            boton = ttk.Button(
                marco, text=texto, command=accion, style=estilo, width=17
            )
            boton.pack(side="left", padx=(0, 8))
            self.botones[clave] = boton

        self.etiqueta_velocidad = ttk.Label(
            marco, style="Dato.TLabel", width=14, anchor="e"
        )
        self.etiqueta_velocidad.pack(side="right")
        self.velocidad = tk.DoubleVar(value=0.45)
        ttk.Scale(
            marco,
            from_=0,
            to=1,
            variable=self.velocidad,
            length=160,
            style="Tarjeta.Horizontal.TScale",
            command=lambda _v: self._actualizar_velocidad(),
        ).pack(side="right", padx=8)
        ttk.Label(marco, text="Velocidad", style="Tarjeta.TLabel").pack(side="right")
        self._actualizar_velocidad()
        return marco

    def _atajos(self) -> None:
        for tecla, accion in (
            ("<space>", self.alternar_reproduccion),
            ("<Right>", self.paso_siguiente),
            ("<Left>", self.paso_anterior),
            ("<Home>", self.reiniciar),
            ("<End>", self.ir_al_final),
            ("<Return>", self.ejecutar),
        ):
            self.raiz.bind(tecla, lambda e, a=accion: self._atajo(e, a))

    def _atajo(self, evento: tk.Event, accion: Callable[[], None]) -> str | None:
        # Los botones y el selector ya responden a sus propias teclas.
        if isinstance(evento.widget, (ttk.Button, ttk.Combobox)):
            return None
        accion()
        return "break"

    # Acciones ---------------------------------------------------------

    def seleccionar_escenario(self) -> None:
        """Muestra los datos del caso elegido y deja la cuadrícula vacía."""
        self._detener()
        self.escenario = self.escenarios[self.claves[self.combo_caso.current()]]()
        self.reproductor = None
        esc = self.escenario
        self.subtitulo.configure(
            text=f"Búsqueda en profundidad con retroceso · Grupo {esc.grupo} · "
            f"{esc.aula} · {len(esc.sesiones)} sesiones en {len(esc.bloques)} bloques"
        )
        self.descripcion.configure(text=self.escenario.descripcion)
        self._llenar_tablas()
        self._crear_celdas()
        self._renderizar()

    def ejecutar(self) -> None:
        """Resuelve el caso y prepara la reproducción desde el paso 0."""
        if self.escenario is None or self.reproductor is not None:
            return
        resultado = AgenteDFS(self.escenario).resolver()
        self.reproductor = Reproductor(resultado)
        self.verificacion_final = verificar(self.escenario, resultado.estado)
        self._renderizar()

    def alternar_reproduccion(self) -> None:
        if self.reproductor is None or self.reproductor.terminado:
            return
        if self.reproduciendo:
            self._detener()
        else:
            self.reproduciendo = True
            self._programar()
        self._renderizar()

    def paso_siguiente(self) -> None:
        self._mover(lambda r: r.avanzar())

    def paso_anterior(self) -> None:
        self._mover(lambda r: r.retroceder())

    def reiniciar(self) -> None:
        self._mover(lambda r: r.reiniciar())

    def ir_al_final(self) -> None:
        self._mover(lambda r: r.ir_al_final())

    def _mover(self, accion: Callable[[Reproductor], object]) -> None:
        if self.reproductor is None:
            return
        self._detener()
        accion(self.reproductor)
        self._renderizar()

    # Reproducción automática ------------------------------------------

    def _pasos_por_segundo(self) -> int:
        escala = VELOCIDAD_MIN * (VELOCIDAD_MAX / VELOCIDAD_MIN) ** self.velocidad.get()
        return max(VELOCIDAD_MIN, round(escala))

    def _actualizar_velocidad(self) -> None:
        self.etiqueta_velocidad.configure(
            text=f"{self._pasos_por_segundo():>5} pasos/s"
        )

    def _programar(self) -> None:
        pasos_s = self._pasos_por_segundo()
        intervalo = max(16, math.ceil(1000 / pasos_s))
        lote = max(1, round(pasos_s * intervalo / 1000))
        self._tarea = self.after(intervalo, lambda: self._tick(lote))

    def _tick(self, lote: int) -> None:
        self._tarea = None
        self.reproductor.avanzar(lote)
        if self.reproductor.terminado:
            self.reproduciendo = False
        else:
            self._programar()
        self._renderizar()

    def _detener(self) -> None:
        if self._tarea is not None:
            self.after_cancel(self._tarea)
            self._tarea = None
        self.reproduciendo = False

    # Dibujo -----------------------------------------------------------

    def _llenar_tablas(self) -> None:
        esc = self.escenario
        self._tabla(
            self.tabla_materias,
            ("ID", "Doc.", "Horas", "Materia"),
            [
                (m.id, m.docente, "+".join(map(str, m.duraciones)), m.nombre)
                for m in esc.materias
            ],
            (26, 26, 48, 130),
        )
        dias = list(dict.fromkeys(b.dia for b in esc.bloques))
        filas = []
        for docente in esc.docentes:
            ocupados = [
                (d, b) for doc, d, b in esc.ocupaciones_docentes if doc == docente
            ]
            por_dia = []
            for dia in dias:
                numeros = sorted(b[1:] for d, b in ocupados if d == dia)
                if numeros:
                    por_dia.append(f"{dia}: {' '.join(numeros)}")
            filas.append((docente, str(len(ocupados)), " | ".join(por_dia)))
        self._tabla(
            self.tabla_ocupaciones,
            ("Doc.", "Total", "Día: bloques ocupados"),
            filas,
            (26, 34, 170),
        )

    def _crear_celdas(self) -> None:
        for hijo in self.rejilla.winfo_children():
            hijo.destroy()
        self.celdas.clear()
        esc = self.escenario
        dias = list(dict.fromkeys(b.dia for b in esc.bloques))
        ids_bloque = list(dict.fromkeys(b.id for b in esc.bloques))
        horas = {b.id: f"{b.hora_inicio[:2]}–{b.hora_fin[:2]}" for b in esc.bloques}
        self.color_materia = {
            m.id: COLOR_MATERIA[i % len(COLOR_MATERIA)]
            for i, m in enumerate(esc.materias)
        }

        for c, dia in enumerate(dias, start=1):
            tk.Label(
                self.rejilla,
                text=dia,
                bg=COLOR["tarjeta"],
                fg=COLOR["texto"],
                font=self.fuentes["seccion"],
            ).grid(row=0, column=c, pady=(0, 4))
        for f, bloque_id in enumerate(ids_bloque, start=1):
            tk.Label(
                self.rejilla,
                text=f"{bloque_id}\n{horas[bloque_id]}",
                bg=COLOR["tarjeta"],
                fg=COLOR["texto_suave"],
                font=self.fuentes["pequena"],
                justify="right",
            ).grid(row=f, column=0, sticky="e", padx=(0, 6))
        for bloque in esc.bloques:
            ocupados = sorted(
                d for d, dia, b in esc.ocupaciones_docentes if (dia, b) == bloque.clave
            )
            texto = "Ocup.: " + " ".join(ocupados) if ocupados else ""
            celda = CeldaHorario(self.rejilla, self.fuentes, texto)
            celda.grid(
                row=ids_bloque.index(bloque.id) + 1,
                column=dias.index(bloque.dia) + 1,
                padx=2,
                pady=2,
            )
            self.celdas[bloque.etiqueta] = celda

    def _renderizar(self) -> None:
        rep = self.reproductor
        listo = rep is not None
        foco = rep.foco if listo else None

        for etiqueta, celda in self.celdas.items():
            asignada = rep.asignaciones.get(etiqueta) if listo else None
            en_foco = (
                foco is not None
                and foco.bloque is not None
                and foco.bloque.etiqueta == etiqueta
            )
            estado = self._estado_foco(foco) if en_foco else None
            if asignada is not None:
                celda.mostrar(
                    asignada.id,
                    asignada.materia.nombre,
                    self.color_materia[asignada.materia.id],
                    estado,
                )
            elif en_foco:  # Candidato que no está (o ya no está) en el horario.
                celda.mostrar(
                    foco.sesion.id, foco.sesion.materia.nombre, COLOR["tarjeta"], estado
                )
            else:
                celda.mostrar("", "", COLOR["tarjeta"], None)

        total = rep.total if listo else 0
        indice = rep.indice if listo else 0
        self.etiqueta_paso.configure(
            text=(
                f"Paso {indice:,} de {total:,}"
                if listo
                else "Ejecuta la búsqueda para empezar"
            )
        )
        self.barra.configure(maximum=max(total, 1), value=indice)
        n_sesiones = len(self.escenario.sesiones)
        self.valores["explorados"].configure(
            text=f"{rep.explorados:,}" if listo else "—"
        )
        self.valores["retrocesos"].configure(
            text=f"{rep.retrocesos:,}" if listo else "—"
        )
        self.valores["colocadas"].configure(
            text=f"{rep.colocadas} / {n_sesiones}" if listo else f"0 / {n_sesiones}"
        )
        nivel = "—"
        if foco is not None and foco.sesion is not None:
            nivel = f"{foco.nivel} ({foco.sesion.id})"
        self.valores["nivel"].configure(text=nivel)
        self.ultimo_paso.configure(text=describir(foco) if foco else "—")

        self.bitacora.delete(0, "end")
        if listo:
            for linea in rep.bitacora:
                self.bitacora.insert("end", linea)
            self.bitacora.see("end")

        self._renderizar_verificacion()
        self._actualizar_botones()

    @staticmethod
    def _estado_foco(foco) -> tuple[str, str]:
        """Texto y color de la etiqueta del paso actual, p. ej. 'RECHAZO R1·M1.2'."""
        texto, color = ESTADO_FOCO[foco.tipo]
        if foco.tipo is TipoEvento.RECHAZAR:
            return f"{texto} {foco.motivo.value[:2]}·{foco.sesion.id}", color
        return f"{texto}·{foco.sesion.id}", color

    def _renderizar_verificacion(self) -> None:
        rep = self.reproductor
        if rep is None or not rep.terminado:
            self.verificacion.configure(
                text="Disponible al terminar la reproducción.",
                fg=COLOR["texto_suave"],
                bg=COLOR["fondo"],
            )
            return
        v = self.verificacion_final
        tiempo_ms = rep.resultado.metricas.tiempo_segundos * 1000
        if v.valido:
            encabezado, color = "Horario válido", COLOR["exito"]
        elif rep.resultado.encontrado:
            encabezado, color = "Horario con conflictos", COLOR["error"]
        else:
            encabezado, color = "Sin solución", COLOR["error"]
        self.verificacion.configure(
            fg="#FFFFFF",
            bg=color,
            text=(
                f"{encabezado}\n"
                f"Materias completas: {v.materias_asignadas} / {v.total_materias}\n"
                f"Conflictos: {len(v.conflictos)}\n"
                f"Tiempo de búsqueda: {tiempo_ms:.1f} ms"
            ),
        )

    def _actualizar_botones(self) -> None:
        rep = self.reproductor
        listo = rep is not None
        self.boton_ejecutar.state(["disabled"] if listo else ["!disabled"])
        hay_atras = listo and rep.indice > 0
        hay_adelante = listo and not rep.terminado
        for clave, activo in (
            ("reiniciar", hay_atras),
            ("anterior", hay_atras),
            ("reproducir", hay_adelante),
            ("siguiente", hay_adelante),
            ("final", hay_adelante),
        ):
            self.botones[clave].state(["!disabled"] if activo else ["disabled"])
        self.botones["reproducir"].configure(
            text="Pausar [Espacio]" if self.reproduciendo else "Reproducir [Espacio]"
        )


def main() -> None:
    raiz = tk.Tk()
    raiz.title("Horario académico sin conflictos — DFS con retroceso")
    raiz.minsize(1360, 800)
    Aplicacion(raiz)
    raiz.mainloop()
