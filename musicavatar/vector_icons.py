"""Iconos vectoriales locales basados en trazos geométricos simples (sin emoji)."""
from __future__ import annotations
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

SHAPES = {
    'play': '<polygon points="8 5 19 12 8 19 8 5"/>',
    'pause': '<rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/>',
    'next': '<polygon points="5 5 15 12 5 19 5 5"/><path d="M19 5v14"/>',
    'previous': '<polygon points="19 5 9 12 19 19 19 5"/><path d="M5 5v14"/>',
    'shuffle': '<path d="M17 3h4v4M3 17l6-6m3 2 9 8m0 0h-4m4 0v-4M3 7h4c6 0 6 10 12 10M14 7c2-3 4-4 7-4"/>',
    'repeat': '<path d="M17 2l4 4-4 4M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4m14-1v2a3 3 0 0 1-3 3H3"/>',
    'heart': '<path d="M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 1 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z"/>',
    'volume': '<polygon points="4 9 8 9 13 5 13 19 8 15 4 15 4 9"/><path d="M17 9c2 2 2 4 0 6m2-9c4 4 4 8 0 12"/>',
    'search': '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l6 6"/>',
    'close': '<path d="M5 5l14 14M19 5L5 19"/>',
}


def icon(name: str, color='#e8dfef', size=28) -> QIcon:
    shape = SHAPES[name]
    # SVG local; se procesa una sola vez al crear el icono.
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">'
           f'<g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
           f'{shape}</g></svg>')
    # Triángulos y rectángulos de reproducción precisan relleno.
    if name in ('play', 'pause', 'next', 'previous'):
        svg = svg.replace('fill="none"', f'fill="{color}"').replace('<path d="M19 5v14"/>','<path d="M19 5v14" fill="none"/>').replace('<path d="M5 5v14"/>','<path d="M5 5v14" fill="none"/>')
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')))
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    return QIcon(pm)
