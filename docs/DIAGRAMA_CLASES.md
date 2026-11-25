# Musicavatar — Diagrama de clases UML (implementación actual)

**Alcance:** código fuente de Musicavatar v0.5 y módulos de colaboración preparados para su integración.  
**Responsables:** Rafael Gabriel Jiménez Espinosa (núcleo), Christofer Alberto Rodríguez Ocaña (créditos) y Ángel Mario Presenda Alpuche (fondos personalizados).

> Este diagrama se obtuvo del **código implementado**. Es apto para documentar la Unidad 5, pero **no sustituye automáticamente** al diagrama que el docente pidió recuperar de la Unidad 4. Si ese documento anterior existe, contrastar sus clases y registrar ajustes en `MATRIZ_TRAZABILIDAD.md`.

## 1. Diagrama principal: reproductor y avatar

![Diagrama principal de clases de Musicavatar](DIAGRAMA_CLASES_PRINCIPAL.png)

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
        +all_tracks()
        +get_track(track_id)
        +set_mood(track_id, mood)
        +set_genres(ids, genres)
        +create_playlist(name)
        +add_many_to_playlist(playlist_id, ids)
        +top_tracks(limit)
        +top_playlists(limit)
        +get_setting(key, default)
        +set_setting(key, value)
    }
    class AudioPlayer {
        +str path
        +bool is_playing
        +load_and_play(path)
        +toggle_pause()
        +seek(seconds)
        +set_volume(volume)
        +stop()
    }
    class PlaybackQueue {
        +list items
        +int current_index
        +list history
        +replace(track_ids)
        +extend(track_ids)
        +select(tid, queue_index, history_cursor)
        +next_target(shuffle, repeat)
        +previous_target(shuffle, repeat)
        +clear()
    }
    class MoodSession {
        +str mood
        +float seconds
        +update(mood, seconds, playing)
        +int stage
    }
    class AvatarLook {
        +str hair
        +str outfit
        +str accessory
        +str hair_style
        +str top_style
        +str pants
        +str shoes
        +str skin
        +str presentation
        +validated()
    }
    class AvatarCanvas {
        +str mood
        +int stage
        +bool playing
        +AvatarLook look
        +set_state(mood, stage, playing)
        +set_customization(hair, outfit, accessory)
        +set_background_image(pixmap, fit, dim)
    }
    class TrackModel {
        +set_tracks(tracks)
        +replace_track(track)
    }
    class TrackFilter {
        +set_context(tab, playlist_ids)
        +set_filters(query, genre, artist, album, mood)
    }
    class MusicavatarWindow {
        +MusicDatabase db
        +AudioPlayer player
        +PlaybackQueue playback
        +MoodSession session
        +import_paths(paths)
        +play_track(tid, queue_index, history_cursor)
        +play_all(shuffle, source)
        +refresh_library(reset_queue)
        +next_track()
        +previous_track()
        +change_track_mood()
    }

    MusicavatarWindow --> MusicDatabase : consulta y guarda
    MusicavatarWindow --> AudioPlayer : controla
    MusicavatarWindow --> PlaybackQueue : administra
    MusicavatarWindow --> MoodSession : contabiliza
    MusicavatarWindow --> AvatarCanvas : actualiza
    MusicavatarWindow --> TrackModel : muestra
    TrackModel --> Track : presenta
    MusicDatabase --> Track : persiste
    TrackFilter --> TrackModel : filtra
    AvatarCanvas *-- AvatarLook : apariencia
```

**Otros componentes usados por la ventana:** `AmbientPanel` (`backdrop.py`, fondo ambiental), `SpectrumWidget` (`spectrum.py`, visualizador), `PlaylistCard` (`playlist_cards.py`, tarjetas) y `TrackMetadataDialog` (`dialogs.py`, edición de etiquetas). No se dibujan todos para mantener legible la relación principal de las clases.

## 2. Diagrama de los paquetes del equipo

![Diagrama de clases de los módulos del equipo](DIAGRAMA_CLASES_EQUIPO.png)

```mermaid
classDiagram
    class MusicavatarWindow {
        +MusicDatabase db
        +AvatarCanvas avatar
        +show_customizer()
    }
    class CreditsDialog {
        +CreditsDialog(parent)
        +accept()
    }
    class BackgroundControls {
        +Path background_file
        +choose_image()
        +reset_background()
        +save_options()
        +_load_saved()
        +_apply_image()
    }
    class AvatarCanvas {
        +set_background_image(pixmap, fit, dim)
    }
    class MusicDatabase {
        +get_setting(key, default)
        +set_setting(key, value)
    }

    MusicavatarWindow ..> CreditsDialog : abre Créditos
    MusicavatarWindow o-- BackgroundControls : agrega a Personalizar
    BackgroundControls --> AvatarCanvas : muestra el fondo
    BackgroundControls --> MusicDatabase : lee y guarda ajustes
```

**Funciones complementarias (no son clases UML):**

- `musicavatar/team_bridge.py` → `install_team_modules(window)`: detecta e instala los módulos opcionales.
- `musicavatar/contrib/credits.py` → `install(window)`: agrega el botón **Créditos** y abre `CreditsDialog`.
- `musicavatar/contrib/credits_info.py`: constantes del proyecto y `members_text()`.
- `musicavatar/contrib/avatar_backgrounds.py` → `install(window)`: incorpora `BackgroundControls` en Personalizar.
- `musicavatar/contrib/background_rules.py` → `validate_image_path()`, `normalize_fit()`, `clamp_dim()` y `stored_background_path()`.
- `musicavatar/metadata.py` → `read_track()` y `scan_paths()`; `musicavatar/moods.py` → `get_track_mood()` y `mood_from_genre()`.

## 3. Descripción breve de las relaciones

- `MusicavatarWindow` coordina la biblioteca, la cola, el audio y los estados del avatar; **no** almacena los archivos musicales dentro de la base de datos.
- `MusicDatabase` almacena rutas, metadatos y preferencias; reconstruye instancias `Track` al consultar.
- `AvatarCanvas` usa un objeto `AvatarLook` para dibujar el personaje por capas.
- `CreditsDialog` es un diálogo opcional, cargado por el puente de integración.
- `BackgroundControls` cambia **únicamente el escenario del avatar**, lee ajustes en `MusicDatabase` y transmite una imagen a `AvatarCanvas`.

## 4. Correspondencia con archivos

| Clase | Archivo de implementación | Responsable |
|---|---|---|
| `Track`, `MusicDatabase`, `AudioPlayer`, `PlaybackQueue`, `MoodSession`, `AvatarLook`, `AvatarCanvas`, `TrackModel`, `TrackFilter`, `MusicavatarWindow` | `musicavatar/models.py`, `database.py`, `player.py`, `queue_logic.py`, `moods.py`, `avatar_parts.py`, `avatar.py`, `track_table.py`, `ui.py` | Rafael |
| `CreditsDialog` | `musicavatar/contrib/credits.py` | Christofer |
| `BackgroundControls` | `musicavatar/contrib/avatar_backgrounds.py` | Ángel Mario |

**Estado actual:** las clases principales están en v0.5. Las clases de Créditos y Fondos están en los módulos preparados por el equipo; confirmar que sus Pull Requests están fusionados antes de marcar su integración como terminada.
