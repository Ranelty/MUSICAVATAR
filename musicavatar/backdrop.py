"""Gradiente ambiente con centro oscuro. Pintura estática y ligera (sin animación)."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QLinearGradient
from PySide6.QtWidgets import QWidget

COLORS = {
    'neutral': '#543362',
    'happy': '#b37b27',
    'sad': '#315f98',
    'calm': '#367f78',
    'energy': '#9f4b42',
    'love': '#954b77',
}
TILES = {
    'neutral': '#ae83c4', 'happy': '#e9b45c', 'sad': '#6fa1d5',
    'calm': '#64bcae', 'energy': '#de8076', 'love': '#d78fb6',
}


class AmbientPanel(QWidget):
    def __init__(self, role='center', parent=None):
        super().__init__(parent)
        self.role = role
        self.mood = 'neutral'
        self.theme_color = '#543362'
        self.setAutoFillBackground(False)

    def set_mood(self, mood):
        if mood != self.mood:
            self.mood = mood
            self.update()

    def set_theme_color(self, color):
        self.theme_color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        main = QColor(self.theme_color if self.mood == 'neutral' else COLORS.get(self.mood, COLORS['neutral']))
        if self.role == 'right':
            main = main.darker(118)
        gradient = QLinearGradient(0, 0, 0, max(1, self.height()))
        gradient.setColorAt(0.0, main)
        gradient.setColorAt(0.25, QColor('#211a29'))
        gradient.setColorAt(0.49, QColor('#17131e'))
        gradient.setColorAt(0.66, QColor('#17131e'))
        gradient.setColorAt(1.0, main.darker(110))
        p.fillRect(self.rect(), gradient)
        color = QColor(TILES.get(self.mood, TILES['neutral']))
        color.setAlpha(65)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        for i, j in ((0,0),(2,0),(3,1),(5,2),(1,3),(4,4)):
            p.drawRect(self.width()-122+i*19, 18+j*19, 11, 11)
        for i, j in ((0,0),(2,0),(1,1),(3,2),(0,3),(4,3)):
            p.drawRect(14+i*19, self.height()-110+j*19, 11, 11)
        if self.role == 'right':
            p.fillRect(0, 0, 1, self.height(), QColor('#54415d'))
        p.end()
