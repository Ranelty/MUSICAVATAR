# Musicavatar — Matriz de trazabilidad diseño → código

**Unidad 5: construcción y verificación.** La columna «Elemento del diseño» corresponde al diagrama **reconstruido a partir del código actual** en `docs/DIAGRAMA_CLASES.md`. Falta contrastar con el diagrama histórico de la **Unidad 4**, si existe, antes de declarar correspondencia exacta entre ambas unidades.

## 1. Núcleo desarrollado por Rafael Gabriel Jiménez Espinosa

| Elemento del diseño | Archivo / clase en código | Estado | Justificación técnica del ajuste |
|---|---|---|---|
| Canción local: `Track` | `musicavatar/models.py → Track` | Implementado | Modelo de datos separado de la reproducción: ruta, título, artista, álbum, género, duración, portada y preferencias. |
| Biblioteca y persistencia | `musicavatar/database.py → MusicDatabase` | Implementado | SQLite almacena información y relaciones sin copiar audio dentro de la base. |
| Importación `add_track()` / `all_tracks()` | `musicavatar/database.py → MusicDatabase` | Implementado | Registra pistas, evita duplicados por ruta y permite cargar la biblioteca. |
| Controles `load_and_play()` / `toggle_pause()` / `seek()` | `musicavatar/player.py → AudioPlayer` | Implementado | La reproducción se encapsula en una clase y verifica la existencia del archivo. |
| Cola e historial `next_target()` / `previous_target()` | `musicavatar/queue_logic.py → PlaybackQueue` | Ajustado | Se separó el historial real del orden de la cola para respaldar aleatorio y retroceso correcto. |
| Estado emocional `update()` / `stage` | `musicavatar/moods.py → MoodSession` | Implementado | Acumula tiempo solo durante reproducción y expone etapas de 0, 15 y 30 minutos. |
| Apariencia `validated()` | `musicavatar/avatar_parts.py → AvatarLook` | Ajustado | Modelo de rasgos validado; permite cabello, ropa, pantalones, zapatos, piel y presentación. |
| Escenario y avatar `set_state()` | `musicavatar/avatar.py → AvatarCanvas` | Implementado | Dibuja personaje con capas y actualiza emoción sin reemplazar el motor de audio. |
| Tabla `set_tracks()` / `replace_track()` | `musicavatar/track_table.py → TrackModel` | Ajustado | Modelo Qt para actualizar filas y evitar reconstrucciones excesivas. |
| Filtrado `set_filters()` | `musicavatar/track_table.py → TrackFilter` | Ajustado | Permite búsqueda y filtros por género, artista, álbum y emoción. |
| Flujo completo `import_paths()` / `play_track()` | `musicavatar/ui.py → MusicavatarWindow` | Implementado | Coordina importación, validación, selección, cola, audio y respuesta visual. |
| Etiquetas y portadas locales | `musicavatar/metadata.py → read_track()` | Implementado | Lectura de metadatos de archivos sin catálogo musical remoto. |
| Escritura de metadatos | `musicavatar/metadata_edit.py → write_file_tags()` | Ajustado | Permite actualizar etiquetas del archivo original en formatos admitidos; comprobar en Windows cada formato. |
| Fondo ambiental general | `musicavatar/backdrop.py → AmbientPanel` | Ajustado | Degradados por estado emocional sin modificar barra lateral ni escenario del avatar. |
| Visualizador de frecuencias | `musicavatar/spectrum.py → SpectrumWidget` | Ajustado | Control opcional 32/64 barras; se puede desactivar para evitar carga innecesaria. |

## 2. Aportaciones de compañeros (paquetes listos; fusión por comprobar)

| Elemento del diseño | Archivo / clase en código | Estado | Justificación técnica del ajuste |
|---|---|---|---|
| Créditos: ventana `CreditsDialog` | `musicavatar/contrib/credits.py → CreditsDialog` | Implementado en módulo independiente | Ventana modal con información del proyecto, equipo y tecnologías. **Integración en GitHub pendiente de verificar.** |
| Datos de créditos y autores | `musicavatar/contrib/credits_info.py → TEAM_MEMBERS` | Implementado en módulo independiente | Centraliza datos para reducir duplicaciones y facilitar pruebas. |
| Controles de fondo `BackgroundControls` | `musicavatar/contrib/avatar_backgrounds.py → BackgroundControls` | Implementado en módulo independiente | El fondo del personaje se personaliza sin modificar el tema de toda la app. **Integración en GitHub pendiente de verificar.** |
| Validación de imagen | `musicavatar/contrib/background_rules.py → validate_image_path()` | Implementado en módulo independiente | Verifica archivo, extensión, tamaño; normaliza ajuste y oscurecimiento. |
| Recepción de imagen personalizada | `musicavatar/avatar.py → AvatarCanvas.set_background_image()` | Ajustado mediante puente de integración | Reutiliza el lienzo del avatar y mantiene el escenario original como alternativa. |
| Carga opcional de contribuciones | `musicavatar/team_bridge.py → install_team_modules()`; `main.py` | Ajustado mediante puente de integración | Desacopla las aportaciones de `ui.py` y permite que la aplicación abra aunque falte un módulo. |

## 3. Estado de comparación con Unidad 4

**Aún no verificable:** el diagrama original de la Unidad 4 no se ha proporcionado para comparar nombres, métodos, relaciones y atributos. Por honestidad académica, los términos «Implementado» y «Ajustado» anteriores describen el **diseño del software incluido**, no prueban por sí solos cambios históricos respecto a la Unidad 4.

Para cerrar la trazabilidad histórica, obtener ese diagrama y completar esta tabla:

| Elemento original de Unidad 4 | Equivalencia en el diseño actual | ¿Hubo cambio? | Justificación del cambio |
|---|---|---|---|
| *Pendiente de incorporar del documento original* | *Clase y método actuales* | *Sí / No* | *Razón técnica real, no hipotética* |

**Caso de uso trazado:** selección de archivos locales → `scan_paths` / `read_track` → `MusicDatabase.add_track` → `MusicavatarWindow.play_track` → `AudioPlayer.load_and_play` → `get_track_mood` → `AvatarCanvas.set_state`.
