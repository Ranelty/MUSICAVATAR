# Musicavatar — Matriz de trazabilidad Diseño → Código

**Importante:** esta es la relación exacta entre el diseño propuesto (`DIAGRAMA_CLASES.md`) y el código incluido. No se recibió aquí el diagrama realizado previamente en la Unidad 4, por lo que **hay que compararlo y completar la columna de ajustes reales** antes de entregar al docente.

| Elemento del diseño (clase / método) | Archivo / clase en código | Estado | Justificación técnica del ajuste |
|---|---|---|---|
| `Track`: id, path, title, artist, album, genre, duration, cover, mood_override, favorite, play_count | `musicavatar/models.py` → `Track` | Implementado | Coincide con el diagrama propuesto; modela una canción local. |
| `MusicDatabase.add_track()` | `musicavatar/database.py` → `MusicDatabase.add_track()` | Implementado | Registra y evita duplicados por ruta única. |
| `MusicDatabase.all_tracks()` | `musicavatar/database.py` → `MusicDatabase.all_tracks()` | Implementado | Recupera la biblioteca para la tabla y la cola. |
| `MusicDatabase.set_mood()` | `musicavatar/database.py` → `MusicDatabase.set_mood()` | Implementado | Guarda preferencia emocional manual por pista. |
| `AudioPlayer.load_and_play()` | `musicavatar/player.py` → `AudioPlayer.load_and_play()` | Implementado | Valida archivo y usa LibVLC o Qt Multimedia. |
| `AudioPlayer.toggle_pause()` | `musicavatar/player.py` → `AudioPlayer.toggle_pause()` | Implementado | Controla pausa sin perder la canción. |
| `MoodSession.update()` y `stage` | `musicavatar/moods.py` → `MoodSession` | Implementado | Acumula segundos solamente durante reproducción; 15 y 30 minutos activan estados. |
| `AvatarCanvas.set_state()` | `musicavatar/avatar.py` → `AvatarCanvas.set_state()` | Implementado | Cambia escena pixel art según emoción y reproducción. |
| `MusicavatarWindow.import_paths()` | `musicavatar/ui.py` → `MusicavatarWindow.import_paths()` | Implementado | Caso de uso: seleccionar, validar e importar música. |
| `MusicavatarWindow.play_track()` | `musicavatar/ui.py` → `MusicavatarWindow.play_track()` | Implementado | Caso de uso: reproducir y actualizar la interfaz. |
| `metadata.read_track()` | `musicavatar/metadata.py` → `read_track()` | Implementado | Función de apoyo para etiquetas y portada. |
| `PlaybackQueue.next_target()` / `previous_target()` | `musicavatar/queue_logic.py` → `PlaybackQueue` | Ajustado | Nuevo controlador de cola: permite historial real en aleatorio y vueltas sin repetir. |
| `TrackModel` / `TrackFilter` | `musicavatar/track_table.py` | Ajustado | Modelo y proxy Qt evitan regenerar toda la tabla para navegar y filtrar. |
| `MusicDatabase.add_many_to_playlist()` | `musicavatar/database.py` | Ajustado | Una sola transacción para varias pistas, conservando su orden. |
| `MusicDatabase.top_tracks()` / `top_playlists()` | `musicavatar/database.py` | Ajustado | Estadísticas de reproducción del Inicio; columnas nuevas migradas desde v0.1. |
| `genres.normalize_genres()` | `musicavatar/genres.py` | Ajustado | Admite y normaliza múltiples géneros por pista. |
| `AmbientPanel.set_mood()` | `musicavatar/backdrop.py` | Ajustado | Fondo coloreado con cuadros estáticos, sin repintar estilos completos ni cargar efectos. |
| `moods.mood_from_genre()` | `musicavatar/moods.py` → `mood_from_genre()` | Implementado | Detección inicial mediante etiquetas de género; sin IA. |

## Ajustes respecto del diseño original de Unidad 4

**Por completar con el equipo.** Si el diseño de Unidad 4 decía, por ejemplo, que una sola clase `Cancion` reprodujera audio, podría justificarse separar `Track` (datos), `AudioPlayer` (motor) y `MusicavatarWindow` (controlador). No reportar ese cambio como hecho histórico sin confirmar el diagrama original.

### Ampliación v0.5 — personalización del personaje

| Elemento de diseño | Archivo/clase en código | Estado | Justificación |
|---|---|---|---|
| Modelo de personaje con rasgos personalizables | `avatar_parts.py → AvatarLook` | Implementado | Atributos separados para cada prenda/rasgo; validación de opciones. |
| Dibujo del personaje por capas | `avatar_parts.py → draw_character()` y `avatar.py → AvatarCanvas` | Ajustado | El avatar anterior solo cambiaba tres rasgos; ahora es modular y conserva estados emocionales. |
| Pantalla de personalización | `ui.py → _build_custom_panel()` | Ajustado | Más opciones, panel desplazable y vista previa sin reemplazar la cola permanentemente. |
| Persistencia de rasgos | `ui.py → _apply_customization()`; `database.py → set_setting()` | Implementado | Se reutiliza SQLite existente, sin migración ni borrado de canciones. |
