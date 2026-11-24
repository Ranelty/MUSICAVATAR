"""Lectura segura de etiquetas y carátulas sin servicios de música externos."""
from __future__ import annotations
from hashlib import sha1
from pathlib import Path
import re
import base64
from .genres import normalize_genres

SUPPORTED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.oga', '.m4a', '.aac', '.opus', '.wma'}


def _first(value, fallback='') -> str:
    if value is None:
        return fallback
    if isinstance(value, (list, tuple)):
        value = value[0] if value else fallback
    return str(value).strip() or fallback


def read_track(path: Path, covers_dir: Path) -> dict:
    """Retorna metadatos incluso si el archivo carece de etiquetas."""
    from mutagen import File as MutagenFile
    path = path.resolve()
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f'Formato no compatible: {path.suffix or "sin extensión"}')
    if not path.is_file():
        raise FileNotFoundError(f'El archivo ya no existe: {path.name}')
    easy = None
    raw = None
    try:
        easy = MutagenFile(str(path), easy=True)
    except Exception:
        pass
    try:
        raw = MutagenFile(str(path))
    except Exception:
        pass
    get = lambda key, fallback='': _first(easy.get(key), fallback) if easy else fallback
    title = get('title', path.stem.replace('_', ' '))
    artist = get('artist', 'Artista desconocido')
    album = get('album', 'Álbum desconocido')
    genre = normalize_genres(easy.get('genre', []) if easy else [])
    duration = float(getattr(getattr(raw, 'info', None), 'length', 0) or 0)
    cover = _extract_cover(path, raw, covers_dir)
    return dict(path=str(path), title=title, artist=artist, album=album, genre=genre,
                duration=duration, cover=cover)


def _extract_cover(path: Path, raw, covers_dir: Path) -> str:
    """Prioriza arte incrustado; luego cover/folder.jpg en la misma carpeta."""
    data = None
    ext = 'jpg'
    if raw is not None:
        try:
            pictures = getattr(raw, 'pictures', None)
            if pictures:
                data = pictures[0].data
                ext = 'png' if 'png' in pictures[0].mime else 'jpg'
            if data is None and raw.tags:
                tags = raw.tags
                # ID3/APIC (MP3, WAV con ID3)
                if hasattr(tags, 'getall'):
                    aps = tags.getall('APIC')
                    if aps:
                        data = aps[0].data
                        ext = 'png' if 'png' in aps[0].mime else 'jpg'
                # OGG/OPUS: carátula embebida codificada en base64.
                if data is None and 'metadata_block_picture' in tags:
                    from mutagen.flac import Picture
                    picture = Picture(base64.b64decode(tags['metadata_block_picture'][0]))
                    data = picture.data
                    ext = 'png' if picture.mime == 'image/png' else 'jpg'
                # MP4/M4A
                if data is None and 'covr' in tags:
                    pictures = tags['covr']
                    if pictures:
                        data = bytes(pictures[0])
                        ext = 'png' if data.startswith(b'\x89PNG') else 'jpg'
        except Exception:
            pass
    if data:
        if len(data) > 15 * 1024 * 1024:
            return ''
        covers_dir.mkdir(parents=True, exist_ok=True)
        digest = sha1(f'{path}|{path.stat().st_mtime_ns}'.encode()).hexdigest()[:20]
        name = covers_dir / f'{digest}.{ext}'
        if not name.exists():
            name.write_bytes(data)
        return str(name)
    for name in ('cover.jpg', 'cover.png', 'folder.jpg', 'folder.png', 'front.jpg', 'front.png'):
        candidate = path.parent / name
        if candidate.is_file():
            return str(candidate)
    return ''


def scan_paths(paths: list[Path]) -> list[Path]:
    """Lee archivos o carpetas recursivamente; evita duplicados de ruta."""
    found = set()
    for path in paths:
        try:
            if path.is_file():
                if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    found.add(path.resolve())
            elif path.is_dir():
                for file in path.rglob('*'):
                    if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
                        found.add(file.resolve())
        except (OSError, PermissionError):
            continue
    return sorted(found, key=lambda p: str(p).casefold())
