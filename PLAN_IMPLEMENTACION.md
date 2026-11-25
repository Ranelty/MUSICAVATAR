# Musicavatar — Plan de implementación (Unidad 5)

**Asignatura:** Ingeniería de Software II  
**Actividad:** De la Arquitectura al Código Ejecutable: Fase de Construcción  
**Lenguaje:** Python  
**Equipo:** Rafael Gabriel Jiménez Espinosa, Christofer Alberto Rodríguez Ocaña y Ángel Mario Presenda Alpuche.

## 1. Estrategia de construcción: abajo hacia arriba (bottom-up)

1. Primero se programaron los modelos de datos (`Track`), el acceso a SQLite (`MusicDatabase`) y las rutinas para leer archivos musicales y sus metadatos.
2. Después se integraron el motor de audio (`AudioPlayer`), la cola (`PlaybackQueue`) y el cálculo de estados emocionales (`MoodSession`), con validaciones y pruebas unitarias.
3. Finalmente se conectaron los módulos a la interfaz (`MusicavatarWindow`), el avatar (`AvatarCanvas`) y las extensiones independientes del equipo.

Esta estrategia permite verificar cada componente antes de usarlo en la interfaz gráfica.

## 2. Distribución definitiva de responsabilidades

| Integrante | Área asignada | Archivos y evidencia de aportación |
|---|---|---|
| **Rafael Gabriel Jiménez Espinosa** | Desarrollo principal, coordinación e integración de componentes | `musicavatar/models.py`, `database.py`, `player.py`, `queue_logic.py`, `moods.py`, `avatar.py`, `avatar_parts.py`, `ui.py`, `main.py`, `team_bridge.py` y pruebas del núcleo; participación acreditada por sus commits. |
| **Christofer Alberto Rodríguez Ocaña** | Créditos y apartado «Acerca de» | `musicavatar/contrib/credits.py`, `credits_info.py`, `tests/test_contrib_credits.py` y `GUIA_COMPANERO_1_CREDITOS.md`; commit y Pull Request propios. |
| **Ángel Mario Presenda Alpuche** | Fondos personalizados del avatar | `musicavatar/contrib/avatar_backgrounds.py`, `background_rules.py`, `tests/test_contrib_backgrounds.py` y `GUIA_COMPANERO_2_FONDOS.md`; commit y Pull Request propios. |

**Estado de integración:** los dos módulos complementarios fueron preparados en paquetes independientes; su incorporación efectiva al repositorio y la autoría de los commits deben verificarse en GitHub. No presentar un archivo o commit de otra persona como evidencia propia.

## 3. Caso de uso completo: importar y reproducir canción local

**Actor principal:** usuario.  
**Precondición:** Musicavatar está abierto, el motor de audio está disponible y el archivo existe en el dispositivo.

1. El usuario selecciona **Importar carpeta** o **Añadir archivos**.
2. `metadata.scan_paths()` localiza archivos compatibles y `metadata.read_track()` lee duración, título, artista, álbum, géneros y portada cuando están disponibles.
3. `MusicDatabase.add_track()` registra las canciones en la biblioteca y controla duplicados.
4. `MusicavatarWindow.refresh_library()` presenta los resultados y permite filtrar.
5. El usuario elige una canción o pulsa **Reproducir todo**; `PlaybackQueue` organiza el orden de reproducción.
6. `MusicavatarWindow.play_track()` llama a `AudioPlayer.load_and_play()`.
7. `get_track_mood()` interpreta el género o la preferencia manual; `AvatarCanvas.set_state()` actualiza el personaje sin detener el audio.

**Salidas:** audio reproducido, nombre/artista/portada de la canción, tiempo de reproducción, cola y estado visual del avatar.

**Errores controlados:** archivos inexistentes, rutas sin música, formatos no compatibles, fallos del motor de audio, nombres de lista vacíos o duplicados, imágenes de fondo inválidas.

## 4. Casos de uso complementarios del equipo

**Créditos (Christofer):** abrir la opción **Créditos** de la barra lateral y consultar integrantes, versión, descripción y tecnologías; cerrar la ventana sin afectar la reproducción.

**Fondo del avatar (Ángel Mario):** abrir **Personalizar**, seleccionar PNG/JPG/WEBP local, escoger **Rellenar** o **Ajustar**, ajustar oscurecimiento, persistir opciones y restaurar el escenario predeterminado. El fondo del avatar es independiente del tema general del reproductor.

## 5. Entregables

- Código completo ejecutable en el repositorio compartido.
- Diagrama de clases y correspondencia diseño-código en `docs/`.
- Matriz de trazabilidad con implementaciones y ajustes documentados.
- Tres capturas **reales** de ejecución: dos operaciones exitosas y una que muestre manejo de error.
- Al menos un commit **real** de cada integrante, visible en GitHub.
- Pruebas unitarias y pruebas manuales de integración.

