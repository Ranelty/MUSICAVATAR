# Propuesta UML — Musicavatar

Este diagrama refleja la implementación de esta entrega. Si el equipo tiene un diagrama de clases de Unidad 4 anterior, **debe reconciliar los dos** y registrar ajustes en la matriz de trazabilidad.

```mermaid
classDiagram
    class Track {
      +int id
      +str path
      +str title
      +str artist
      +str album
      +str genre
      +float duration
      +str cover
      +str mood_override
      +bool favorite
      +int play_count
      +bool exists
    }
    class MusicDatabase {
      +add_track(data)
      +all_tracks() list~Track~
      +get_track(id) Track
      +set_mood(id, mood)
      +set_genres(ids, genres)
      +set_moods(ids, mood)
      +top_tracks(limit)
      +top_playlists(limit)
      +add_many_to_playlist(pid, ids)
      +toggle_favorite(id) bool
      +create_playlist(name) bool
      +add_to_playlist(playlist_id, track_id)
    }
    class AudioPlayer {
      +load_and_play(path) bool
      +toggle_pause()
      +seek(seconds)
      +set_volume(volume)
      +stop()
    }
    class MoodSession {
      +str mood
      +float seconds
      +update(mood, seconds, playing)
      +int stage
    }
    class AvatarCanvas {
      +str mood
      +int stage
      +bool playing
      +set_state(mood, stage, playing)
      +set_customization(hair, outfit, accessory)
    }
    class PlaybackQueue {
      +list~int~ items
      +int current_index
      +list history
      +replace(ids)
      +extend(ids)
      +next_target(shuffle, repeat)
      +previous_target(shuffle, repeat)
    }
    class TrackModel {
      +set_tracks(tracks)
      +replace_track(track)
    }
    class TrackFilter {
      +set_context(tab, playlist_ids)
      +set_filters(query, genre, artist, album, mood)
    }
    class AmbientPanel {
      +set_mood(mood)
    }
    class MusicavatarWindow {
      +import_paths(paths)
      +play_track(id)
      +toggle_play()
      +next_track()
      +change_track_mood()
      +refresh_library()
      +play_all(shuffle)
      +previous_track()
    }
    MusicavatarWindow --> MusicDatabase
    MusicavatarWindow --> AudioPlayer
    MusicavatarWindow --> PlaybackQueue
    MusicavatarWindow --> TrackModel
    TrackModel --> Track
    TrackFilter --> TrackModel
    MusicavatarWindow --> TrackFilter
    MusicavatarWindow --> AmbientPanel
    MusicavatarWindow --> AvatarCanvas
    MusicavatarWindow --> MoodSession
    MusicDatabase --> Track
    MusicavatarWindow --> Track
```

**Funciones asociadas:** `metadata.read_track(path,covers_dir)` extrae etiquetas; `moods.mood_from_genre(genre)` clasifica el género y `moods.get_track_mood(track)` aplica una modificación manual si existe; `utils.format_time(seconds)` formatea el tiempo y `genres.normalize_genres()` admite varias etiquetas de género.

### Ampliación del avatar en v0.5

- `AvatarLook` (en `musicavatar/avatar_parts.py`): modelo inmutable con atributos `hair`, `outfit`, `accessory`, `hair_style`, `top_style`, `pants`, `shoes`, `skin`, `presentation`. El método `validated()` protege contra configuraciones desconocidas y conserva valores legados.
- `draw_character(painter, x, y, look, mood, playing, tick, glow)` (en `musicavatar/avatar_parts.py`): dibuja las capas individuales de personaje, rostro, ropa y accesorios con píxeles.
- `AvatarCanvas` (en `musicavatar/avatar.py`): representa `AvatarLook` en el mundo del avatar, soporta `preview=True` sin animación constante y expone `set_customization()`.
- `MusicavatarWindow` (en `musicavatar/ui.py`): crea los controles del panel, observa cambios, actualiza las dos vistas y persiste los campos en `MusicDatabase.settings`.

Relación: `MusicavatarWindow` configura `AvatarLook` mediante `AvatarCanvas`; `AvatarCanvas` delega a `draw_character`. El diseño es extensible y no afecta `AudioPlayer`.
