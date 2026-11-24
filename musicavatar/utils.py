"""Funciones pequeñas fáciles de mantener y probar entre integrantes."""
from pathlib import Path


def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds or 0))
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f'{hours}:{minutes:02d}:{sec:02d}'
    return f'{minutes}:{sec:02d}'


def safe_filename(path: str) -> str:
    return Path(path).stem.replace('_', ' ') or 'Sin título'
