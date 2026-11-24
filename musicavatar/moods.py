"""Reglas ligeras para categorizar géneros, sin IA ni conexión a internet.

MÓDULO PARA COLABORADORES: se pueden ampliar los géneros sin modificar el reproductor.
"""
from __future__ import annotations
from dataclasses import dataclass
from .genres import split_genres

MOODS = {
    'neutral': {'label': 'Neutral', 'accent': '#b99de9', 'tint': '#17131f', 'message': 'Esperando tu música'},
    'happy': {'label': 'Alegre', 'accent': '#efc76b', 'tint': '#29231b', 'message': '¡Qué buen ritmo!'},
    'sad': {'label': 'Melancólico', 'accent': '#88a9ee', 'tint': '#18212e', 'message': 'Día de nostalgia'},
    'calm': {'label': 'Tranquilo', 'accent': '#9bbec0', 'tint': '#172524', 'message': 'Momento para relajarse'},
    'energy': {'label': 'Enérgico', 'accent': '#eb916f', 'tint': '#291a22', 'message': '¡Sube el volumen!'},
    'love': {'label': 'Romántico', 'accent': '#e5a0b9', 'tint': '#291c26', 'message': 'Corazón en modo musical'},
}

# Orden de prioridad: primero coincidencias específicas y luego etiquetas generales.
GENRE_RULES = {
    'sad': ('sad', 'melanchol', 'emo', 'sadcore', 'slowcore', 'depress', 'sad pop', 'triste'),
    'calm': ('lo-fi', 'lofi', 'chill', 'ambient', 'meditation', 'downtempo', 'new age', 'relax', 'classical', 'acoustic', 'jazz'),
    'energy': ('metal', 'hard rock', 'j-rock', 'punk', 'hardcore', 'drum and bass', 'dubstep', 'techno', 'edm', 'trap', 'phonk', 'rock', 'rap', 'hip-hop'),
    'love': ('romantic', 'romance', 'ballad', 'balada', 'love song', 'soul'),
    'happy': ('happy', 'upbeat', 'dance', 'disco', 'funk', 'salsa', 'merengue', 'cumbia', 'k-pop', 'j-pop', 'pop', 'reggaeton'),
}


def mood_from_genre(genre: str | None) -> str:
    if not genre:
        return 'neutral'
    genres = [part.casefold() for part in split_genres(genre)]
    for mood, terms in GENRE_RULES.items():
        if any(term in part for term in terms for part in genres):
            return mood
    return 'neutral'


def get_track_mood(track) -> str:
    if track is None:
        return 'neutral'
    override = getattr(track, 'mood_override', '') or ''
    if override in MOODS:
        return override
    return mood_from_genre(getattr(track, 'genre', ''))


@dataclass
class MoodSession:
    mood: str = 'neutral'
    seconds: float = 0.0

    def update(self, mood: str, seconds: float, playing: bool) -> None:
        """Cuenta solo tiempo de música realmente reproducida."""
        if mood != self.mood:
            self.mood = mood
            self.seconds = 0
        if playing and seconds > 0:
            self.seconds += min(seconds, 2.5)

    @property
    def stage(self) -> int:
        if self.seconds >= 30 * 60:
            return 2
        if self.seconds >= 15 * 60:
            return 1
        return 0
