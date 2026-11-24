"""SQLite local Musicavatar. Migraciones aditivas compatibles con v0.1/0.2."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from .models import Track

TRACK_COLUMNS = 'id,path,title,artist,album,genre,duration,cover,mood_override,favorite,play_count'


class MusicDatabase:
    def __init__(self, location: Path):
        location.parent.mkdir(parents=True, exist_ok=True)
        self.location = location
        self.conn = sqlite3.connect(str(location))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys = ON')
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            artist TEXT NOT NULL DEFAULT 'Artista desconocido',
            album TEXT NOT NULL DEFAULT 'Álbum desconocido',
            genre TEXT NOT NULL DEFAULT '',
            duration REAL NOT NULL DEFAULT 0,
            cover TEXT NOT NULL DEFAULT '',
            mood_override TEXT NOT NULL DEFAULT '',
            favorite INTEGER NOT NULL DEFAULT 0,
            play_count INTEGER NOT NULL DEFAULT 0,
            added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            play_count INTEGER NOT NULL DEFAULT 0,
            cover TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS playlist_tracks (
            playlist_id INTEGER NOT NULL,
            track_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (playlist_id, track_id),
            FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
            FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS mood_totals (
            mood TEXT PRIMARY KEY,
            seconds REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        ''')
        # Una instalación v0.1 existente no se borra: solo se añaden las columnas faltantes.
        for table in ('tracks', 'playlists'):
            fields = {row['name'] for row in self.conn.execute(f'PRAGMA table_info({table})')}
            if 'play_count' not in fields:
                self.conn.execute(f'ALTER TABLE {table} ADD COLUMN play_count INTEGER NOT NULL DEFAULT 0')
        fields = {row['name'] for row in self.conn.execute('PRAGMA table_info(playlists)')}
        if 'cover' not in fields:
            self.conn.execute("ALTER TABLE playlists ADD COLUMN cover TEXT NOT NULL DEFAULT ''")
        self.conn.commit()

    def add_track(self, data: dict) -> tuple[int, bool]:
        found = self.conn.execute('SELECT id FROM tracks WHERE path=?', (data['path'],)).fetchone()
        if found:
            return int(found['id']), False
        fields = ('path', 'title', 'artist', 'album', 'genre', 'duration', 'cover')
        values = [data.get(field, '') for field in fields]
        cursor = self.conn.execute('INSERT INTO tracks (' + ','.join(fields) + ') VALUES (?,?,?,?,?,?,?)', values)
        self.conn.commit()
        return int(cursor.lastrowid), True

    @staticmethod
    def _to_track(row) -> Track:
        d = dict(row)
        d['favorite'] = bool(d.get('favorite'))
        return Track(**{k: d[k] for k in Track.__dataclass_fields__ if k in d})

    def all_tracks(self) -> list[Track]:
        return [self._to_track(row) for row in self.conn.execute(f'SELECT {TRACK_COLUMNS} FROM tracks ORDER BY title COLLATE NOCASE')]

    def get_track(self, track_id: int) -> Track | None:
        row = self.conn.execute(f'SELECT {TRACK_COLUMNS} FROM tracks WHERE id=?', (track_id,)).fetchone()
        return self._to_track(row) if row else None

    def update_track_metadata(self, track_id: int, data: dict):
        """Actualiza solo etiquetas. Conserva favoritos, reproducciones y emoción manual."""
        fields = ('title','artist','album','genre','duration','cover')
        with self.conn:
            self.conn.execute('UPDATE tracks SET '+ ','.join(f'{k}=?' for k in fields) +
                              ' WHERE id=?', tuple(data.get(k,'') for k in fields)+(track_id,))

    def update_track_path(self, track_id: int, new_path: str):
        """Conserva el ID, las playlists, favoritos y estadísticas al renombrar."""
        with self.conn:
            self.conn.execute('UPDATE tracks SET path=? WHERE id=?', (new_path, track_id))

    def set_mood(self, track_id: int, mood: str):
        self.set_moods([track_id], mood)

    def set_moods(self, ids: list[int], mood: str):
        with self.conn:
            self.conn.executemany('UPDATE tracks SET mood_override=? WHERE id=?', ((mood, i) for i in dict.fromkeys(ids)))

    def set_genres(self, ids: list[int], genres: str):
        with self.conn:
            self.conn.executemany('UPDATE tracks SET genre=? WHERE id=?', ((genres, i) for i in dict.fromkeys(ids)))

    def set_favorites(self, ids: list[int], favorite: bool):
        with self.conn:
            self.conn.executemany('UPDATE tracks SET favorite=? WHERE id=?', ((int(favorite), i) for i in dict.fromkeys(ids)))

    def toggle_favorite(self, track_id: int) -> bool:
        old = self.get_track(track_id)
        if old is None:
            return False
        new = not old.favorite
        self.set_favorites([track_id], new)
        return new

    def remove_track(self, track_id: int):
        self.remove_tracks([track_id])

    def remove_tracks(self, ids: list[int]):
        with self.conn:
            self.conn.executemany('DELETE FROM tracks WHERE id=?', ((i,) for i in dict.fromkeys(ids)))

    def increment_track_play(self, track_id: int):
        with self.conn:
            self.conn.execute('UPDATE tracks SET play_count=play_count+1 WHERE id=?', (track_id,))

    def top_tracks(self, limit: int = 3) -> list[Track]:
        rows = self.conn.execute(f'SELECT {TRACK_COLUMNS} FROM tracks WHERE play_count>0 ORDER BY play_count DESC, title COLLATE NOCASE LIMIT ?', (limit,)).fetchall()
        return [self._to_track(row) for row in rows]

    def create_playlist(self, name: str) -> bool:
        name = name.strip()
        if not name:
            return False
        try:
            with self.conn:
                self.conn.execute('INSERT INTO playlists (name) VALUES (?)', (name,))
            return True
        except sqlite3.IntegrityError:
            return False

    def playlist_details(self) -> list[tuple[int, str, str, int, int]]:
        rows = self.conn.execute('''
        SELECT p.id, p.name, p.cover, p.play_count, COUNT(pt.track_id) AS songs
        FROM playlists p LEFT JOIN playlist_tracks pt ON pt.playlist_id=p.id
        GROUP BY p.id ORDER BY p.name COLLATE NOCASE
        ''').fetchall()
        return [(int(r['id']),r['name'],r['cover'],int(r['play_count']),int(r['songs'])) for r in rows]

    def set_playlist_cover(self, playlist_id: int, cover: str):
        with self.conn:
            self.conn.execute('UPDATE playlists SET cover=? WHERE id=?',(cover,playlist_id))

    def get_playlist_cover(self, playlist_id: int) -> str:
        row = self.conn.execute('SELECT cover FROM playlists WHERE id=?',(playlist_id,)).fetchone()
        return row['cover'] if row else ''

    def mood_totals(self) -> dict[str,float]:
        return {r['mood']:float(r['seconds']) for r in self.conn.execute('SELECT mood,seconds FROM mood_totals')}

    def add_mood_seconds(self, mood: str, seconds: float):
        if seconds <= 0:
            return
        with self.conn:
            self.conn.execute('''
              INSERT INTO mood_totals(mood,seconds) VALUES (?,?)
              ON CONFLICT(mood) DO UPDATE SET seconds=seconds+excluded.seconds
            ''',(mood,seconds))

    def playlists(self) -> list[tuple[int, str]]:
        return [(int(r['id']), r['name']) for r in self.conn.execute('SELECT id,name FROM playlists ORDER BY name COLLATE NOCASE')]

    def top_playlists(self, limit: int = 3) -> list[tuple[int, str, int]]:
        return [(int(r['id']), r['name'], int(r['play_count'])) for r in self.conn.execute('SELECT id,name,play_count FROM playlists WHERE play_count>0 ORDER BY play_count DESC, name COLLATE NOCASE LIMIT ?', (limit,))]

    def increment_playlist_play(self, playlist_id: int):
        with self.conn:
            self.conn.execute('UPDATE playlists SET play_count=play_count+1 WHERE id=?', (playlist_id,))

    def add_to_playlist(self, playlist_id: int, track_id: int):
        self.add_many_to_playlist(playlist_id, [track_id])

    def add_many_to_playlist(self, playlist_id: int, ids: list[int]) -> int:
        """Una transacción para toda la selección, manteniendo el orden."""
        unique = list(dict.fromkeys(ids))
        if not unique:
            return 0
        current = self.conn.execute('SELECT COALESCE(MAX(position),0) FROM playlist_tracks WHERE playlist_id=?', (playlist_id,)).fetchone()[0]
        added = 0
        with self.conn:
            for tid in unique:
                cur = self.conn.execute('INSERT OR IGNORE INTO playlist_tracks (playlist_id,track_id,position) VALUES (?,?,?)', (playlist_id,tid,current+1))
                if cur.rowcount:
                    current += 1
                    added += 1
        return added

    def playlist_track_ids(self, playlist_id: int | None) -> list[int]:
        if playlist_id is None:
            return []
        return [int(r['track_id']) for r in self.conn.execute('SELECT track_id FROM playlist_tracks WHERE playlist_id=? ORDER BY position, track_id', (playlist_id,))]

    def get_setting(self, key: str, default: str = '') -> str:
        row = self.conn.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
        return row['value'] if row else default

    def set_setting(self, key: str, value: str):
        with self.conn:
            self.conn.execute('INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, value))

    def close(self):
        self.conn.close()
