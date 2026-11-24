"""Tarjetas ligeras para el explorador de listas. Cargan la miniatura una sola vez."""
from __future__ import annotations
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from .vector_icons import icon


class PlaylistCard(QFrame):
    opened = Signal(int)
    play_requested = Signal(int, bool)
    cover_requested = Signal(int)

    def __init__(self, playlist_id: int, name: str, song_count: int, cover: QPixmap, parent=None):
        super().__init__(parent)
        self.playlist_id = playlist_id
        self.setObjectName('PlaylistCard')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedWidth(180)
        self.setMinimumHeight(230)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12,12,12,12)
        layout.setSpacing(8)
        image = QLabel()
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setPixmap(cover)
        image.setFixedHeight(142)
        layout.addWidget(image)
        heading = QLabel(name)
        heading.setWordWrap(True)
        heading.setStyleSheet('font-weight:bold;font-size:13px')
        layout.addWidget(heading)
        caption = QLabel(f'{song_count} canciones')
        caption.setObjectName('Muted')
        layout.addWidget(caption)
        action_row = QHBoxLayout()
        action_row.setSpacing(5)
        self.play_button = QPushButton()
        self.play_button.setIcon(icon('play'))
        self.play_button.setToolTip('Reproducir lista')
        self.play_button.clicked.connect(lambda: self.play_requested.emit(self.playlist_id,False))
        self.random_button = QPushButton()
        self.random_button.setIcon(icon('shuffle'))
        self.random_button.setToolTip('Reproducir lista en aleatorio')
        self.random_button.clicked.connect(lambda: self.play_requested.emit(self.playlist_id,True))
        self.image_button = QPushButton('Portada…')
        self.image_button.setToolTip('Cambiar miniatura de la lista')
        self.image_button.clicked.connect(lambda: self.cover_requested.emit(self.playlist_id))
        for btn in (self.play_button,self.random_button,self.image_button):
            btn.setFixedHeight(30)
            action_row.addWidget(btn)
            btn.hide()
        layout.addLayout(action_row)

    def enterEvent(self,event):
        for widget in (self.play_button,self.random_button,self.image_button):
            widget.show()
        super().enterEvent(event)

    def leaveEvent(self,event):
        for widget in (self.play_button,self.random_button,self.image_button):
            widget.hide()
        super().leaveEvent(event)

    def mouseReleaseEvent(self,event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.opened.emit(self.playlist_id)
        super().mouseReleaseEvent(event)
