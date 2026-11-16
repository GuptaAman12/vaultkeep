"""Gradient strength bar with level markers for password dialogs."""

import tkinter as tk

from .theme import BORDER, MUTED, SURFACE, TEXT, FONT_SMALL, FONT_SMALL_BOLD


def _blend(first, second, amount):
    """Blend two hex colors."""
    channels = []
    for offset in (1, 3, 5):
        a = int(first[offset:offset + 2], 16)
        b = int(second[offset:offset + 2], 16)
        channels.append(round(a + (b - a) * amount))
    return "#{:02x}{:02x}{:02x}".format(*channels)


class StrengthMeter(tk.Frame):
    """A red-to-green gradient bar with five marked strength levels."""

    STOPS = (
        (0.0, "#d32f2f"),
        (0.25, "#f57c00"),
        (0.5, "#fbc02d"),
        (0.75, "#7cb342"),
        (1.0, "#388e3c"),
    )
    MARKS = ("W", "F", "G", "S", "VS")

    def __init__(self, parent):
        super().__init__(parent, bg=SURFACE, highlightthickness=0)
        self.canvas = tk.Canvas(self, height=38, bg=SURFACE, highlightthickness=0)
        self.canvas.pack(fill="x", expand=True)
        self.canvas.bind("<Configure>", self._draw)
        self.caption = tk.Label(self, text=" ", bg=SURFACE, fg=MUTED,
                                font=FONT_SMALL_BOLD, anchor="w")
        self.caption.pack(fill="x")
        self.level = 0
        self._draw()

    def set(self, level, text=""):
        """Move the pointer to a strength level from 0 to 4."""
        self.level = max(0, min(4, level))
        self.caption.config(text=text or " ", fg=self._color(self.level / 4))
        self._draw()

    def _color(self, position):
        for (start, first), (end, second) in zip(self.STOPS, self.STOPS[1:]):
            if position <= end:
                return _blend(first, second, (position - start) / (end - start))
        return self.STOPS[-1][1]

    def _draw(self, event=None):
        width = self.canvas.winfo_width()
        if width < 30:
            return
        self.canvas.delete("all")
        top, height = 7, 11

        for x in range(width):
            self.canvas.create_line(
                x, top, x, top + height, fill=self._color(x / max(width - 1, 1)))
        self.canvas.create_rectangle(0, top, width - 1, top + height, outline=BORDER)

        for index, mark in enumerate(self.MARKS):
            x = round(index * (width - 1) / 4)
            self.canvas.create_line(x, top + height + 2, x, top + height + 6, fill=MUTED)
            label_x = min(max(x, 10), width - 10)
            self.canvas.create_text(label_x, 31, text=mark, fill=MUTED, font=FONT_SMALL)

        pointer = min(max(round(self.level * (width - 1) / 4), 6), width - 7)
        self.canvas.create_polygon(
            pointer - 6, 0, pointer + 6, 0, pointer, top - 1, fill=TEXT)
