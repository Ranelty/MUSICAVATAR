"""Validaciones puras y configuración de fondos de avatar (sin PySide6)."""
from __future__ import annotations
from pathlib import Path

ALLOWED_EXTENSIONS = frozenset({'.png', '.jpg', '.jpeg', '.webp'})
MAX_BYTES = 15 * 1024 * 1024
DEFAULT_FIT = 'cover'
DEFAULT_DIM = 0


def validate_image_path(path: str | Path) -> Path:
    p = Path(path).expanduser()
    if p.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError('Formato inválido. Utiliza PNG, JPG, JPEG o WEBP.')
    if not p.is_file():
        raise ValueError('La imagen seleccionada no existe.')
    if p.stat().st_size > MAX_BYTES:
        raise ValueError('La imagen supera el límite de 15 MB.')
    if p.stat().st_size == 0:
        raise ValueError('La imagen está vacía.')
    return p


def normalize_fit(value: str) -> str:
    return value if value in ('cover', 'contain') else DEFAULT_FIT


def clamp_dim(value: int | str) -> int:
    try:
        return max(0, min(80, int(value)))
    except (TypeError, ValueError):
        return DEFAULT_DIM


def stored_background_path(project_root: Path) -> Path:
    return project_root / 'data' / 'avatar_backgrounds' / 'scene.png'
