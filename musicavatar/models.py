from dataclasses import dataclass

@dataclass(slots=True)
class Track:
    """Representa una canción importada de un archivo local."""
    id: int
    path: str
    title: str
    artist: str = 'Artista desconocido'
    album: str = 'Álbum desconocido'
    genre: str = ''
    duration: float = 0.0
    cover: str = ''
    mood_override: str = ''
    favorite: bool = False
    play_count: int = 0

    @property
    def exists(self) -> bool:
        from pathlib import Path
        return Path(self.path).is_file()
