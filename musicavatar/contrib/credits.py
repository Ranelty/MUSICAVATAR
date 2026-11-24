"""Contribución 1: botón Créditos y ventana Acerca de Musicavatar.

Se instala desde musicavatar.team_bridge sin editar la interfaz principal.
"""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton, QFrame, QVBoxLayout, QHBoxLayout,
)
from musicavatar.dialogs import exec_blurred
from .credits_info import (
    PROJECT_NAME, PROJECT_VERSION, PROJECT_DESCRIPTION,
    TEAM_MEMBERS, TECHNOLOGIES,
)


class CreditsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Créditos · Musicavatar')
        self.setMinimumSize(460, 420)
        self.setModal(True)
        self.setObjectName('CreditsDialog')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 22, 25, 20)
        layout.setSpacing(12)
        heading = QLabel('♫  ' + PROJECT_NAME)
        heading.setStyleSheet('font-size:25px;font-weight:700;color:#d6b6fa;')
        layout.addWidget(heading)
        version = QLabel('ACERCA DEL PROYECTO  ·  ' + PROJECT_VERSION)
        version.setObjectName('Muted')
        layout.addWidget(version)
        intro = QLabel(PROJECT_DESCRIPTION)
        intro.setWordWrap(True)
        layout.addWidget(intro)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)
        title = QLabel('EQUIPO DE DESARROLLO')
        title.setStyleSheet('font-weight:700;color:#c4a4ec;')
        layout.addWidget(title)
        for n, name in enumerate(TEAM_MEMBERS, start=1):
            row = QHBoxLayout()
            dot = QLabel(f'{n:02d}')
            dot.setStyleSheet('color:#ac8ed3;min-width:32px;font-weight:700;')
            row.addWidget(dot)
            member = QLabel(name)
            member.setWordWrap(True)
            row.addWidget(member, 1)
            layout.addLayout(row)
        layout.addSpacing(4)
        stack = QLabel('Tecnologías: ' + ' · '.join(TECHNOLOGIES))
        stack.setWordWrap(True)
        stack.setObjectName('Muted')
        layout.addWidget(stack)
        layout.addStretch()
        close = QPushButton('Cerrar')
        close.setObjectName('Primary')
        close.clicked.connect(self.accept)
        layout.addWidget(close)


def install(window):
    """Inserta Créditos debajo de Configuraciones sin tocar ui.py."""
    sidebar = window.centralWidget().layout().itemAt(0).widget()
    layout = sidebar.layout()
    button = QPushButton('ⓘ   Créditos')
    button.setObjectName('NavButton')
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setProperty('active', False)
    index = layout.indexOf(window.nav_buttons['Configuraciones'])
    layout.insertWidget(index + 1, button)
    window.nav_buttons['Créditos'] = button

    def show_credits():
        window._set_active_nav(button, True)
        try:
            exec_blurred(CreditsDialog(window), window)
        finally:
            window._set_active_nav(button, False)

    button.clicked.connect(show_credits)
    return button
