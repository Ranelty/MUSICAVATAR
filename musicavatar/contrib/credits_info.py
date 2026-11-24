"""Datos de créditos aprobados para el proyecto académico Musicavatar.

Mantenerlos aquí permite comprobarlos sin iniciar la interfaz gráfica.
"""
from __future__ import annotations

PROJECT_NAME = 'Musicavatar'
PROJECT_VERSION = '0.5 + módulos de equipo'
PROJECT_DESCRIPTION = (
    'Reproductor de música local con avatar pixel art personalizable, '
    'biblioteca, listas de reproducción y estados emocionales.'
)
TEAM_MEMBERS = (
    'Christofer Alberto Rodríguez Ocaña',
    'Ángel Mario Presenda Alpuche',
    'Rafael Gabriel Jiménez Espinosa',
)
TECHNOLOGIES = ('Python', 'PySide6', 'SQLite', 'Mutagen', 'LibVLC')


def members_text() -> str:
    return '\n'.join(TEAM_MEMBERS)
