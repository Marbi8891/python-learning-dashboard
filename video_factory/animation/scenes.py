"""Componentes reutilizables de Manim. Cada escena se dibuja con los datos de un JSON.

No se ejecuta directamente: `video_factory.render` lanza Manim con la variable de entorno
PLD_SCENE_SPEC apuntando al JSON de la escena (texto ya en el idioma del vídeo, duración real
de la narración y comienzo de cada frase). La escena dura exactamente lo que dura su audio.
"""

from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path

from manim import (
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    LaggedStart,
    Line,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
)
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from video_factory.animation import theme as T

SANS = os.environ.get("PLD_FONT_SANS", "Helvetica Neue")
MONO = os.environ.get("PLD_FONT_MONO", "Menlo")
MIN_RUN = 1 / 15


def label(text: str, size: float = 30, color: str = T.TEXT, bold: bool = False, mono=False):
    """Texto de una línea (nunca vacío: Pango no dibuja cadenas vacías)."""
    options = {"weight": BOLD} if bold else {}
    return Text(
        text or " ",
        font=MONO if mono else SANS,
        font_size=size,
        color=color,
        disable_ligatures=True,
        **options,
    )


def fit(mobject, max_width: float | None = None, max_height: float | None = None):
    """Reduce el objeto si no cabe (nunca lo agranda)."""
    if max_width and mobject.width > max_width:
        mobject.scale(max_width / mobject.width)
    if max_height and mobject.height > max_height:
        mobject.scale(max_height / mobject.height)
    return mobject


def box(width, height, fill=T.SURFACE_2, stroke=T.BORDER, radius=0.16, stroke_width=2.0):
    return RoundedRectangle(
        corner_radius=min(radius, height / 2 - 0.01, width / 2 - 0.01),
        width=width,
        height=height,
        fill_color=fill,
        fill_opacity=1,
        stroke_color=stroke,
        stroke_width=stroke_width,
    )


def chip(text: str, fill=T.PRIMARY, color=T.ON_PRIMARY, size=24, mono=True):
    """Etiqueta redondeada con texto: nombres de variable, tipos, claves…"""
    content = label(text, size, color, bold=True, mono=mono)
    background = box(content.width + 0.5, content.height + 0.32, fill=fill, stroke=fill)
    content.move_to(background)
    return VGroup(background, content)


class CodeBlock(VGroup):
    """Ventana de editor con código resaltado y una barra que señala la línea activa."""

    def __init__(self, code, language="python", width=12.4, max_height=4.6, title="", size=26):
        super().__init__()
        self.lines = code.split("\n")
        self.text = Text(code, font=MONO, font_size=size, color=T.CODE_TEXT, disable_ligatures=True)
        self._colorize(code, language)
        one = Text("Ag", font=MONO, font_size=size)
        two = Text("Ag\nAg", font=MONO, font_size=size)
        pitch = two.height - one.height
        bar_height = 0.5
        scale = min(
            1.0,
            (width - 0.9) / self.text.width,
            (max_height - bar_height - 0.6) / max(self.text.height, 0.01),
        )
        self.text.scale(scale)
        self.pitch = pitch * scale

        height = max(len(self.lines) * self.pitch, self.text.height) + bar_height + 0.6
        self.panel = box(width, height, fill=T.CODE_BG, radius=0.2)
        top_bar = Line(
            self.panel.get_corner(UP + LEFT) + DOWN * bar_height + RIGHT * 0.02,
            self.panel.get_corner(UP + RIGHT) + DOWN * bar_height + LEFT * 0.02,
            color=T.BORDER,
            stroke_width=1.5,
        )
        dots = VGroup(
            *[Dot(radius=0.07, color=color) for color in (T.DANGER, T.PRIMARY, T.ACCENT)]
        ).arrange(RIGHT, buff=0.14)
        dots.move_to(self.panel.get_corner(UP + LEFT) + RIGHT * 0.55 + DOWN * bar_height / 2)
        name = label(title, 18, T.MUTED, mono=True)
        name.move_to(self.panel.get_top() + DOWN * bar_height / 2)

        self.text.align_to(self.panel, LEFT).shift(RIGHT * 0.45)
        first_line_y = self.panel.get_top()[1] - bar_height - 0.3 - self.pitch / 2
        self._anchor_lines(first_line_y)

        self.bar = Rectangle(
            width=width - 0.08,
            height=self.pitch * 1.08,
            fill_color=T.PRIMARY,
            fill_opacity=0,
            stroke_width=0,
        )
        self.marker = Rectangle(
            width=0.07,
            height=self.pitch * 1.08,
            fill_color=T.PRIMARY,
            fill_opacity=0,
            stroke_width=0,
        )
        self.marker.align_to(self.bar, LEFT)
        self.highlight = VGroup(self.bar, self.marker)
        self.highlight.move_to([self.panel.get_center()[0], self.line_y(1), 0])
        self.pointing = False
        self.add(self.panel, top_bar, dots, self.highlight, self.text)
        if title:
            self.add(name)

    def _colorize(self, code: str, language: str) -> None:
        visible = sum(1 for char in code if not char.isspace())
        if len(self.text.submobjects) != visible:
            return  # la fuente unió o separó glifos: se deja el color base antes que colorear mal
        try:
            lexer = get_lexer_by_name(language, stripnl=False, ensurenl=False)
        except ClassNotFound:
            return
        index = 0
        for token_type, value in lex(code, lexer):
            color = T.syntax_color(token_type)
            for char in value:
                if not char.isspace():
                    if index < visible:
                        self.text.submobjects[index].set_color(color)
                    index += 1

    def _anchor_lines(self, first_line_y: float) -> None:
        """Coloca el texto de modo que la línea 1 quede centrada en first_line_y."""
        offsets, index = [], 0
        for number, line in enumerate(self.lines):
            count = sum(1 for char in line if not char.isspace())
            if count and index + count <= len(self.text.submobjects):
                glyphs = VGroup(*self.text.submobjects[index : index + count])
                offsets.append(glyphs.get_center()[1] + number * self.pitch)
            index += count
        offsets.sort()
        current = offsets[len(offsets) // 2] if offsets else self.text.get_top()[1]
        self.text.shift(UP * (first_line_y - current))
        self._first_line_y = first_line_y

    def line_y(self, number: int) -> float:
        return self._first_line_y - (number - 1) * self.pitch

    def shift(self, *vectors):
        before = self.panel.get_center()[1]
        super().shift(*vectors)
        self._first_line_y += self.panel.get_center()[1] - before
        return self

    def point_at(self, number: int) -> list:
        """Animaciones que llevan la barra a la línea indicada (la primera vez, la muestran)."""
        number = max(1, min(number, len(self.lines)))
        target = [self.panel.get_center()[0], self.line_y(number), 0]
        if not self.pointing:
            self.pointing = True
            self.highlight.move_to(target)
            return [
                self.bar.animate.set_fill(opacity=0.16),
                self.marker.animate.set_fill(opacity=1),
            ]
        return [self.highlight.animate.move_to(target)]


class Console(VGroup):
    """Ventana de terminal: las líneas de salida se añaden de una en una."""

    def __init__(self, width=12.4, height=2.0, title="consola", size=24):
        super().__init__()
        self.size = size
        self.panel = box(width, height, fill="#07090c", radius=0.2)
        self.title = label(title, 17, T.MUTED, mono=True)
        self.title.move_to(self.panel.get_corner(UP + LEFT) + RIGHT * (0.4 + self.title.width / 2))
        self.title.shift(DOWN * 0.27)
        self.rows = VGroup()
        self.add(self.panel, self.title, self.rows)

    def new_line(self, text: str, color=T.CODE_TEXT):
        row = label(text, self.size, color, mono=True)
        fit(row, self.panel.width - 0.9)
        top = self.panel.get_top()[1] - 0.62
        row.move_to([0, top - len(self.rows) * 0.46 - 0.12, 0])
        row.align_to(self.panel, LEFT).shift(RIGHT * 0.45)
        self.rows.add(row)
        return row


class FactoryScene(Scene):
    """Base común: carga el JSON, lleva el reloj de la escena y dibuja la cabecera."""

    def setup(self):
        path = os.environ.get("PLD_SCENE_SPEC")
        if not path:
            raise RuntimeError("Falta PLD_SCENE_SPEC: lanza las escenas con `video_factory render`")
        self.spec = json.loads(Path(path).read_text(encoding="utf-8"))
        self.data = self.spec.get("data", {})
        self.steps = self.spec.get("steps", [])
        self.total = float(self.spec["duration"])
        self.sentences = self.spec.get("sentences", [])
        self.clock = 0.0

    def construct(self):
        self.camera.background_color = T.BG
        self.footer()
        self.build()
        self.go_to(self.total)

    # --- reloj ---------------------------------------------------------------------------
    def run(self, *animations, run_time: float = 0.5):
        """Reproduce animaciones sin pasarse del final de la narración."""
        remaining = self.total - self.clock
        run_time = max(min(run_time, remaining - 0.05), MIN_RUN)
        self.play(*animations, run_time=run_time)
        self.clock += run_time

    def go_to(self, moment: float):
        """Espera hasta el segundo indicado de la escena."""
        pause = min(moment, self.total) - self.clock
        if pause >= MIN_RUN:
            self.wait(pause)
            self.clock += pause

    def step_time(self, index: int, count: int | None = None) -> float:
        """Cuándo aparece el paso: con su frase, en su fracción o repartido de forma uniforme."""
        count = count or len(self.steps) or 1
        step = self.steps[index] if index < len(self.steps) else {}
        sentence = step.get("sentence")
        if sentence is not None and sentence < len(self.sentences):
            return max(self.sentences[sentence], 0.2)
        if step.get("at") is not None:
            return step["at"] * self.total
        return 1.0 + index * max(self.total - 2.6, 0.5) / count

    def sentence_time(self, index, default: float) -> float:
        if index is not None and index < len(self.sentences):
            return max(self.sentences[index], 0.2)
        return default

    # --- elementos comunes ---------------------------------------------------------------
    def footer(self):
        """Pie discreto: lección y avance dentro del vídeo."""
        name = label(self.spec.get("lesson_title", ""), 16, T.MUTED)
        fit(name, 7)
        name.move_to([T.LEFT_EDGE + name.width / 2, -3.72, 0])
        track = Line([2.6, -3.72, 0], [T.RIGHT_EDGE, -3.72, 0], color=T.BORDER, stroke_width=4)
        position = self.spec.get("index", 0) + 1
        done = track.get_start() + (track.get_end() - track.get_start()) * (
            position / max(self.spec.get("count", 1), 1)
        )
        progress = Line(track.get_start(), done, color=T.PRIMARY, stroke_width=4)
        self.add(name, track, progress)

    def header(self):
        """Título de la escena arriba a la izquierda, con una línea de acento."""
        heading = label(self.spec.get("heading", ""), 40, T.STRONG, bold=True)
        fit(heading, T.RIGHT_EDGE - T.LEFT_EDGE)
        heading.move_to([T.LEFT_EDGE + heading.width / 2, 3.15, 0])
        accent = Line(
            [T.LEFT_EDGE, 2.62, 0], [T.LEFT_EDGE + 1.1, 2.62, 0], color=T.PRIMARY, stroke_width=6
        )
        self.run(FadeIn(heading, shift=RIGHT * 0.2), Create(accent), run_time=0.5)
        return heading

    def bullet_rows(
        self,
        texts,
        left=T.LEFT_EDGE,
        top=T.BODY_TOP,
        width=12.0,
        check=False,
        size=30,
        bottom=T.BODY_BOTTOM,
    ):
        """Filas de una lista (punto o marca de verificación + texto), sin animar todavía."""
        rows = VGroup()
        wrap_at = max(int(width * 3.3 * 30 / size), 20)
        for text in texts:
            if check:
                mark = VGroup(
                    Circle(radius=0.2, color=T.ACCENT, stroke_width=3),
                    VGroup(
                        Line([-0.09, 0.0, 0], [-0.02, -0.08, 0], color=T.ACCENT, stroke_width=4),
                        Line([-0.02, -0.08, 0], [0.11, 0.09, 0], color=T.ACCENT, stroke_width=4),
                    ),
                )
            else:
                mark = Dot(radius=0.09, color=T.PRIMARY)
            content = Text(
                "\n".join(textwrap.wrap(text, wrap_at)) or " ",
                font=SANS,
                font_size=size,
                color=T.TEXT,
                disable_ligatures=True,
            )
            fit(content, width - 0.8)
            content.next_to(mark, RIGHT, buff=0.35)
            rows.add(VGroup(mark, content))
        rows.arrange(DOWN, buff=0.48, aligned_edge=LEFT)
        fit(rows, max_height=top - bottom)
        rows.move_to([left + rows.width / 2, top - rows.height / 2, 0])
        return rows

    def reveal_rows(self, rows):
        for index, row in enumerate(rows):
            self.go_to(self.step_time(index, len(rows)))
            self.run(FadeIn(row, shift=RIGHT * 0.25), run_time=0.45)

    def step_texts(self) -> list[str]:
        return [step["text"] for step in self.steps if step.get("text")]

    def build(self):
        raise NotImplementedError


class TitleScene(FactoryScene):
    """Introducción: curso, nombre de la lección y línea de acento."""

    def build(self):
        kicker = label(self.data.get("kicker", ""), 26, T.PRIMARY, bold=True)
        title = label(self.spec.get("heading", ""), 76, T.STRONG, bold=True)
        fit(title, 12.2)
        fit(kicker, 12.2)
        accent = Line([-1.2, 0, 0], [1.2, 0, 0], color=T.PRIMARY, stroke_width=8)
        VGroup(kicker, title, accent).arrange(DOWN, buff=0.5)
        brand = label("Python Learning Dashboard", 22, T.MUTED)
        brand.move_to([0, -2.6, 0])
        self.run(FadeIn(kicker, shift=DOWN * 0.2), run_time=0.5)
        self.run(FadeIn(title, shift=UP * 0.25), run_time=0.7)
        self.run(Create(accent), FadeIn(brand), run_time=0.6)


class ConceptScene(FactoryScene):
    """Idea clave con sus puntos, que aparecen al ritmo de la narración."""

    def build(self):
        self.header()
        top = T.BODY_TOP
        emphasis = self.data.get("emphasis")
        if emphasis:
            big = label(emphasis, 44, T.PRIMARY, bold=True, mono=True)
            fit(big, 12)
            big.move_to([T.LEFT_EDGE + big.width / 2, top - big.height / 2, 0])
            self.run(FadeIn(big), run_time=0.5)
            top -= big.height + 0.6
        rows = self.bullet_rows(self.step_texts(), top=top)
        self.reveal_rows(rows)


class CodeScene(FactoryScene):
    """Código en un editor; resalta líneas y, si hay salida, lo ejecuta en la consola."""

    def build(self):
        self.header()
        output = self.spec.get("output", "")
        code = CodeBlock(
            self.spec.get("code", ""),
            self.spec.get("code_language", "python"),
            max_height=3.0 if output else 5.5,
            title=self.data.get("filename", ""),
        )
        code.move_to([0, T.BODY_TOP - code.panel.height / 2, 0])
        self.run(FadeIn(code, shift=UP * 0.15), run_time=0.6)

        caption = None
        run_at = self.sentence_time(self.data.get("run_at_sentence"), self.total * 0.55)
        events = [(self.step_time(i), "step", step) for i, step in enumerate(self.steps)]
        if output:
            events.append((run_at, "run", None))
        for moment, kind, step in sorted(events, key=lambda event: event[0]):
            self.go_to(moment)
            if kind == "run":
                self.execute(code, output)
                continue
            animations = []
            if step.get("line"):
                animations += code.point_at(step["line"])
            if step.get("text"):
                note = label(step["text"], 26, T.MUTED)
                fit(note, 12.2)
                note.move_to([T.LEFT_EDGE + note.width / 2, code.panel.get_bottom()[1] - 0.5, 0])
                if caption is not None:
                    animations.append(FadeOut(caption))
                animations.append(FadeIn(note))
                caption = note
            if animations:
                self.run(*animations, run_time=0.4)

    def execute(self, code: CodeBlock, output: str):
        """La instrucción viaja del editor a Python y el resultado se escribe en la consola."""
        console = Console(height=min(0.95 + 0.46 * len(output.split("\n")), 2.3), title="consola")
        console.move_to([0, T.BODY_BOTTOM + console.panel.height / 2, 0])
        python = chip("Python", fill=T.ACCENT, color="#06130b", size=22, mono=False)
        middle = (code.panel.get_bottom()[1] + console.panel.get_top()[1]) / 2
        python.move_to([0, middle, 0])
        going = Arrow(
            code.panel.get_bottom(), python.get_top(), buff=0.05, color=T.MUTED, stroke_width=4
        )
        coming = Arrow(
            python.get_bottom(), console.panel.get_top(), buff=0.05, color=T.MUTED, stroke_width=4
        )
        self.run(FadeIn(console), FadeIn(python), run_time=0.4)
        self.run(GrowArrow(going), run_time=0.35)
        self.run(Indicate(python, color=T.ACCENT, scale_factor=1.12), run_time=0.45)
        self.run(GrowArrow(coming), run_time=0.35)
        for line in output.split("\n"):
            self.run(FadeIn(console.new_line(line), shift=RIGHT * 0.15), run_time=0.35)


class TerminalScene(FactoryScene):
    """Terminal: se escribe la orden y aparece la salida del programa línea a línea."""

    def build(self):
        self.header()
        output = self.spec.get("output", "")
        lines = output.split("\n") if output else []
        command = self.data.get("command", "")
        rows = len(lines) + (1 if command else 0)
        console = Console(height=min(1.1 + 0.46 * rows, 5.4), title="terminal", size=26)
        console.move_to([0, T.BODY_TOP - console.panel.height / 2, 0])
        self.run(FadeIn(console, shift=UP * 0.15), run_time=0.5)
        if command:
            row = console.new_line(f"$ {command}", T.ACCENT)
            self.run(LaggedStart(*[FadeIn(glyph) for glyph in row], lag_ratio=0.6), run_time=0.9)
        self.go_to(self.sentence_time(self.data.get("output_at_sentence"), 1.6) + 0.6)
        for line in lines:
            self.run(FadeIn(console.new_line(line), shift=RIGHT * 0.15), run_time=0.4)
            self.go_to(self.clock + 0.25)


class VariableScene(FactoryScene):
    """Cada nombre (etiqueta) apunta a un valor (caja). Reasignar cambia el valor de la caja."""

    def build(self):
        self.header()
        assignments = self.data.get("assignments", [])
        names = list(dict.fromkeys(item["name"] for item in assignments))
        spacing = min(1.5, 4.8 / max(len(names), 1))
        row_y = {name: 1.3 - index * spacing for index, name in enumerate(names)}
        code_y = 1.5
        values = {}
        for index, item in enumerate(assignments):
            self.go_to(self.step_time(index, len(assignments)))
            line = label(
                item.get("code", f"{item['name']} = {item['value']}"), 28, T.CODE_TEXT, mono=True
            )
            fit(line, 5.4)
            line.move_to([T.LEFT_EDGE + 0.2 + line.width / 2, code_y - index * 0.75, 0])
            self.run(FadeIn(line, shift=RIGHT * 0.2), run_time=0.4)
            value = label(str(item["value"]), 30, T.STRONG, mono=True)
            y = row_y[item["name"]]
            if item["name"] in values:
                container, old = values[item["name"]]
                fit(value, container.width - 0.4).move_to(container)
                self.run(FadeOut(old, shift=UP * 0.3), FadeIn(value, shift=UP * 0.3), run_time=0.5)
                self.run(Indicate(container, color=T.PRIMARY, scale_factor=1.06), run_time=0.4)
                values[item["name"]] = (container, value)
                continue
            tag = chip(item["name"], size=26)
            tag.move_to([1.2, y, 0])
            container = box(max(value.width + 0.9, 2.2), 1.0)
            container.move_to([4.6, y, 0])
            value.move_to(container)
            pointer = Arrow(
                tag.get_right(), container.get_left(), buff=0.12, color=T.MUTED, stroke_width=4
            )
            self.run(FadeIn(tag, shift=RIGHT * 0.2), run_time=0.35)
            self.run(GrowArrow(pointer), FadeIn(container), run_time=0.4)
            self.run(FadeIn(value), run_time=0.3)
            values[item["name"]] = (container, value)


class DataTypeScene(FactoryScene):
    """Tarjetas con un valor de ejemplo y su tipo."""

    def build(self):
        self.header()
        items = self.data.get("items", [])
        cards = VGroup()
        for item in items:
            value = label(str(item["value"]), 34, T.STRONG, mono=True)
            kind = chip(item["type"], size=22)
            note = label(item.get("note", ""), 20, T.MUTED)
            content = VGroup(value, kind, note).arrange(DOWN, buff=0.35)
            frame = box(max(content.width + 0.8, 2.6), content.height + 0.9)
            content.move_to(frame)
            cards.add(VGroup(frame, content))
        cards.arrange(RIGHT, buff=0.4)
        fit(cards, 12.4).move_to([0, -0.4, 0])
        for index, card in enumerate(cards):
            self.go_to(self.step_time(index, len(cards)))
            self.run(FadeIn(card, shift=UP * 0.2), run_time=0.45)


class ConditionalScene(FactoryScene):
    """Rombo con la condición y dos ramas; se ilumina la que se ejecuta."""

    def build(self):
        self.header()
        condition = label(self.data.get("condition", ""), 26, T.STRONG, mono=True)
        diamond = Polygon(
            [0, 1.0, 0],
            [2.6, 0, 0],
            [0, -1.0, 0],
            [-2.6, 0, 0],
            color=T.PRIMARY,
            stroke_width=3,
            fill_color=T.SURFACE_2,
            fill_opacity=1,
        )
        fit(condition, 3.2).move_to(diamond)
        top = VGroup(diamond, condition).move_to([0, 1.0, 0])
        self.run(FadeIn(top), run_time=0.5)
        branches = self.data.get("branches", [])[:2]
        taken = self.data.get("taken")
        drawn = []
        for index, branch in enumerate(branches):
            side = -1 if index == 0 else 1
            body = label(branch.get("body", ""), 24, T.CODE_TEXT, mono=True)
            frame = box(max(body.width + 0.8, 3.4), 1.1)
            frame.move_to([side * 3.9, -2.1, 0])
            fit(body, frame.width - 0.4).move_to(frame)
            arrow = Arrow(
                diamond.get_center() + side * RIGHT * 2.6,
                frame.get_top(),
                buff=0.1,
                color=T.MUTED,
                stroke_width=4,
            )
            tag = label(branch.get("label", ""), 22, T.MUTED, bold=True)
            tag.next_to(arrow.get_center(), side * RIGHT, buff=0.25)
            drawn.append(VGroup(arrow, tag, frame, body))
        self.go_to(self.step_time(0, 2))
        self.run(*[FadeIn(group) for group in drawn], run_time=0.5)
        if taken is not None and taken < len(drawn):
            self.go_to(self.step_time(1, 2))
            chosen = drawn[taken]
            others = [group.animate.set_opacity(0.3) for i, group in enumerate(drawn) if i != taken]
            self.run(chosen[2].animate.set_stroke(T.ACCENT, width=4), *others, run_time=0.5)
            self.run(Indicate(chosen[3], color=T.ACCENT, scale_factor=1.08), run_time=0.5)


class LoopScene(FactoryScene):
    """Un puntero recorre los elementos; en cada vuelta cambia la variable y hay una salida."""

    def build(self):
        self.header()
        items = [str(item) for item in self.data.get("items", [])]
        variable = self.data.get("variable", "x")
        outputs = [str(item) for item in self.data.get("outputs", [])]
        cells = VGroup()
        for item in items:
            value = label(item, 28, T.STRONG, mono=True)
            frame = box(max(value.width + 0.6, 1.2), 1.0)
            value.move_to(frame)
            cells.add(VGroup(frame, value))
        cells.arrange(RIGHT, buff=0.12)
        fit(cells, 12.2).move_to([0, 1.2, 0])
        self.run(FadeIn(cells), run_time=0.5)
        console = Console(height=min(1.0 + 0.46 * max(len(outputs), 1), 2.6), title="consola")
        console.move_to([0, T.BODY_BOTTOM + console.panel.height / 2, 0])
        if outputs:
            self.run(FadeIn(console), run_time=0.3)
        pointer = Arrow([0, -0.5, 0], [0, 0.5, 0], buff=0, color=T.PRIMARY, stroke_width=6)
        current = label(
            f"{variable} = {items[0]}" if items else variable, 28, T.PRIMARY, bold=True, mono=True
        )
        for index, cell in enumerate(cells):
            self.go_to(self.step_time(index, len(cells)))
            target = cell.get_bottom() + DOWN * 0.55
            text = label(f"{variable} = {items[index]}", 28, T.PRIMARY, bold=True, mono=True)
            text.move_to(target + DOWN * 0.75)
            if index == 0:
                pointer.move_to(target)
                current = text
                self.run(GrowArrow(pointer), FadeIn(current), run_time=0.4)
            else:
                self.run(
                    pointer.animate.move_to(target), FadeOut(current), FadeIn(text), run_time=0.4
                )
                current = text
            self.run(cell[0].animate.set_stroke(T.PRIMARY, width=4), run_time=0.2)
            if index < len(outputs):
                self.run(FadeIn(console.new_line(outputs[index])), run_time=0.25)


class FunctionScene(FactoryScene):
    """La función como una máquina: entran argumentos, sale el valor de retorno."""

    def build(self):
        self.header()
        name = label(f"{self.data.get('name', 'f')}()", 34, T.STRONG, bold=True, mono=True)
        machine = box(max(name.width + 1.2, 4.0), 2.2, stroke=T.PRIMARY, stroke_width=3)
        machine.move_to([0, -0.3, 0])
        name.move_to(machine)
        self.run(FadeIn(machine), FadeIn(name), run_time=0.5)
        arguments = self.data.get("args", [])
        parameters = self.data.get("params", [])
        entries = VGroup()
        for index, argument in enumerate(arguments):
            text = str(argument)
            if index < len(parameters):
                text = f"{parameters[index]} = {argument}"
            entries.add(chip(text, size=24))
        entries.arrange(DOWN, buff=0.3).move_to([-5.0, -0.3, 0])
        fit(entries, 2.8, 3.6)
        self.go_to(self.step_time(0, 2))
        enter = Arrow([-3.5, -0.3, 0], machine.get_left(), buff=0.1, color=T.MUTED, stroke_width=4)
        if len(entries):
            self.run(FadeIn(entries, shift=RIGHT * 0.3), GrowArrow(enter), run_time=0.6)
        self.run(Indicate(machine, color=T.PRIMARY, scale_factor=1.04), run_time=0.5)
        if "result" in self.data:
            self.go_to(self.step_time(1, 2))
            result = chip(str(self.data["result"]), fill=T.ACCENT, color="#06130b", size=26)
            result.move_to([5.0, -0.3, 0])
            leave = Arrow(
                machine.get_right(), result.get_left(), buff=0.1, color=T.MUTED, stroke_width=4
            )
            tag = label("return", 20, T.MUTED, mono=True).next_to(leave, UP, buff=0.1)
            self.run(GrowArrow(leave), FadeIn(tag), run_time=0.4)
            self.run(FadeIn(result, shift=RIGHT * 0.3), run_time=0.4)


class ListScene(FactoryScene):
    """Lista como celdas numeradas desde 0; los pasos señalan posiciones."""

    def build(self):
        self.header()
        items = [str(item) for item in self.data.get("items", [])]
        cells = VGroup()
        for index, item in enumerate(items):
            value = label(item, 28, T.STRONG, mono=True)
            frame = box(max(value.width + 0.6, 1.3), 1.1)
            value.move_to(frame)
            position = label(str(index), 20, T.MUTED, mono=True).next_to(frame, DOWN, buff=0.15)
            cells.add(VGroup(frame, value, position))
        cells.arrange(RIGHT, buff=0.1, aligned_edge=UP)
        fit(cells, 11.0).move_to([0.6, 0.4, 0])
        name = label(self.data.get("name", ""), 28, T.PRIMARY, bold=True, mono=True)
        name.next_to(cells, UP, buff=0.4).align_to(cells, LEFT)
        self.run(FadeIn(name), run_time=0.3)
        self.run(LaggedStart(*[FadeIn(cell) for cell in cells], lag_ratio=0.25), run_time=0.9)
        caption = None
        for index, step in enumerate(self.steps):
            self.go_to(self.step_time(index))
            animations = []
            position = step.get("index")
            if position is not None and position < len(cells):
                for cell in cells:
                    cell[0].set_stroke(T.BORDER, width=2)
                animations.append(cells[position][0].animate.set_stroke(T.PRIMARY, width=5))
            if step.get("text"):
                note = label(step["text"], 28, T.TEXT)
                fit(note, 12.2).move_to([0, -2.3, 0])
                if caption is not None:
                    animations.append(FadeOut(caption))
                animations.append(FadeIn(note))
                caption = note
            if animations:
                self.run(*animations, run_time=0.4)


class DictionaryScene(FactoryScene):
    """Diccionario como filas clave → valor; los pasos señalan una clave."""

    def build(self):
        self.header()
        pairs = self.data.get("pairs", [])
        rows, by_key = VGroup(), {}
        for key, value in pairs:
            tag = chip(str(key), size=24)
            content = label(str(value), 26, T.STRONG, mono=True)
            frame = box(max(content.width + 0.8, 2.4), 0.85)
            content.move_to(frame)
            holder = VGroup(frame, content)
            VGroup(tag, holder).arrange(RIGHT, buff=1.4)
            arrow = Arrow(
                tag.get_right(), holder.get_left(), buff=0.1, color=T.MUTED, stroke_width=3
            )
            row = VGroup(tag, arrow, holder)
            rows.add(row)
            by_key[str(key)] = row
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit(rows, 11.5, 4.6).move_to([0, -0.5, 0])
        name = label(self.data.get("name", ""), 28, T.PRIMARY, bold=True, mono=True)
        name.next_to(rows, UP, buff=0.3).align_to(rows, LEFT)
        self.run(FadeIn(name), run_time=0.3)
        self.run(LaggedStart(*[FadeIn(row) for row in rows], lag_ratio=0.3), run_time=1.0)
        for index, step in enumerate(self.steps):
            row = by_key.get(str(step.get("key")))
            if row is None:
                continue
            self.go_to(self.step_time(index))
            self.run(Indicate(row, color=T.PRIMARY, scale_factor=1.05), run_time=0.6)


class ErrorScene(FactoryScene):
    """Código que falla, el mensaje de error de Python y cómo se arregla."""

    def build(self):
        self.header()
        code = CodeBlock(
            self.spec.get("code", ""), self.spec.get("code_language", "python"), max_height=2.8
        )
        code.move_to([0, T.BODY_TOP - code.panel.height / 2, 0])
        self.run(FadeIn(code), run_time=0.5)
        line = next((step["line"] for step in self.steps if step.get("line")), None)
        self.go_to(self.step_time(0, 3))
        if line:
            code.bar.set_fill(T.DANGER)
            code.marker.set_fill(T.DANGER)
            self.run(*code.point_at(line), run_time=0.4)
        kind = label(self.data.get("error_type", "Error"), 26, T.DANGER, bold=True, mono=True)
        message = label(self.data.get("message", ""), 24, T.TEXT, mono=True)
        content = VGroup(kind, message).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        fit(content, 11.6)
        frame = box(12.4, content.height + 0.6, fill="#2a1416", stroke=T.DANGER)
        frame.move_to([0, code.panel.get_bottom()[1] - 0.35 - frame.height / 2, 0])
        content.move_to(frame).align_to(frame, LEFT).shift(RIGHT * 0.4)
        self.go_to(self.step_time(1, 3))
        self.run(FadeIn(frame), FadeIn(content), run_time=0.5)
        fix = self.data.get("fix")
        if fix:
            self.go_to(self.step_time(2, 3))
            mark = Dot(radius=0.1, color=T.ACCENT)
            text = label(fix, 26, T.ACCENT)
            fit(text, 11.4)
            row = VGroup(mark, text).arrange(RIGHT, buff=0.3)
            row.move_to([T.LEFT_EDGE + row.width / 2, frame.get_bottom()[1] - 0.6, 0])
            self.run(FadeIn(row, shift=UP * 0.15), run_time=0.5)


class ExerciseScene(FactoryScene):
    """Reto para el estudiante: pasos a la izquierda y código de partida a la derecha."""

    def build(self):
        self.header()
        starter = self.spec.get("code", "")
        width = 6.0 if starter else 12.0
        rows = self.bullet_rows(self.step_texts(), width=width, size=28)
        if starter:
            code = CodeBlock(
                starter,
                self.spec.get("code_language", "python"),
                width=6.3,
                max_height=5.2,
                size=22,
            )
            code.move_to(
                [T.RIGHT_EDGE - code.panel.width / 2, T.BODY_TOP - code.panel.height / 2, 0]
            )
            self.run(FadeIn(code, shift=LEFT * 0.2), run_time=0.5)
        self.reveal_rows(rows)


class SummaryScene(FactoryScene):
    """Cierre: lo aprendido, punto por punto, con marca de verificación."""

    def build(self):
        self.header()
        rows = self.bullet_rows(self.step_texts(), check=True)
        self.reveal_rows(rows)


SCENE_CLASSES = {
    "title": TitleScene,
    "concept": ConceptScene,
    "code": CodeScene,
    "terminal": TerminalScene,
    "variable": VariableScene,
    "datatype": DataTypeScene,
    "conditional": ConditionalScene,
    "loop": LoopScene,
    "function": FunctionScene,
    "list": ListScene,
    "dictionary": DictionaryScene,
    "error": ErrorScene,
    "exercise": ExerciseScene,
    "summary": SummaryScene,
}
