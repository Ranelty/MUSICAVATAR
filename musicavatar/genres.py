"""Catálogo editable de géneros: normalización y sugerencias sin servicios externos.

Las etiquetas libres se conservan cuando no hay coincidencia fiable en el catálogo.
Este módulo no intenta adivinar un género a partir del audio.
"""
from __future__ import annotations
from difflib import get_close_matches
import re
import unicodedata

GENRE_CATALOG = (
    'Acoustic', 'Alternative', 'Ambient', 'Anime', 'Balada', 'Blues', 'Bossa Nova',
    'Chill', 'Chiptune', 'Clásica', 'Country', 'Cumbia', 'Dance', 'Disco',
    'Drum and Bass', 'Dubstep', 'EDM', 'Electrónica', 'Emo', 'Folk', 'Funk',
    'Gospel', 'Hard Rock', 'Hip-Hop', 'House', 'Indie', 'Instrumental', 'Jazz',
    'J-Pop', 'J-Rock', 'K-Pop', 'Lo-Fi', 'Metal', 'Orchestral', 'OST', 'Phonk',
    'Pop', 'Punk', 'R&B', 'Rap', 'Reggaetón', 'Rock', 'Salsa', 'Ska', 'Soul',
    'Synthwave', 'Techno', 'Trap', 'Trance', 'Vaporwave', 'Video Game Music',
)


def _key(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    return ''.join(c for c in text if not unicodedata.combining(c)).casefold().strip()


_ALIASES = {
    'lofi': 'Lo-Fi', 'lo fi': 'Lo-Fi', 'lo-fi hip hop': 'Lo-Fi',
    'hip hop': 'Hip-Hop', 'hiphop': 'Hip-Hop',
    'soundtrack': 'OST', 'original soundtrack': 'OST',
    'electronic': 'Electrónica', 'electronica': 'Electrónica',
    'classical': 'Clásica', 'clasica': 'Clásica',
    'reggaeton': 'Reggaetón', 'regueton': 'Reggaetón',
    'jpop': 'J-Pop', 'kpop': 'K-Pop', 'jrock': 'J-Rock',
    'rnb': 'R&B', 'rhythm and blues': 'R&B',
}
_LOOKUP = {_key(x): x for x in GENRE_CATALOG}
_LOOKUP.update(_ALIASES)


def canonical_genre(value: str) -> str:
    cleaned = str(value or '').strip()
    return _LOOKUP.get(_key(cleaned), cleaned)


def split_genres(text: str | list[str] | None) -> list[str]:
    entries = [str(v) for v in text] if isinstance(text, (list, tuple)) else [str(text or '')]
    seen, result = set(), []
    for entry in entries:
        for part in re.split(r'[,;|]+', entry):
            canonical = canonical_genre(part)
            if canonical and _key(canonical) not in seen:
                seen.add(_key(canonical))
                result.append(canonical)
    return result


def normalize_genres(value: str | list[str] | None) -> str:
    return ', '.join(split_genres(value))


def genre_suggestions(query: str, existing=()) -> list[str]:
    """Sugiere nombres, incluyendo una corrección aproximada («roc» → «Rock»)."""
    names = list(dict.fromkeys([*GENRE_CATALOG, *existing]))
    key = _key(query)
    if not key:
        return sorted(names, key=str.casefold)
    starts = [name for name in names if _key(name).startswith(key)]
    contains = [name for name in names if key in _key(name) and name not in starts]
    approximate = get_close_matches(key, [_key(n) for n in names], n=6, cutoff=0.58)
    near = [name for target in approximate for name in names if _key(name) == target]
    return list(dict.fromkeys(starts + contains + near))[:18]


def infer_genre_from_words(*parts: str) -> str:
    """Solo deduce etiquetas inequívocas en el título/álbum/nombre de archivo.

    No sustituye a un clasificador de audio y NO promete géneros reales.
    """
    text = _key(' '.join(parts))
    hints = (
        (r'\b(lo[ -]?fi|chillhop)\b', 'Lo-Fi'),
        (r'\b(soundtrack|original soundtrack|ost)\b', 'OST'),
        (r'\b(chiptune|8[ -]?bit)\b', 'Chiptune'),
        (r'\b(synthwave|vaporwave|phonk|j[ -]?rock|j[ -]?pop|k[ -]?pop)\b', None),
    )
    for pattern, genre in hints:
        match = re.search(pattern, text)
        if match:
            return genre or canonical_genre(match.group(0))
    return ''
