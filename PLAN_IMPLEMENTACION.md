# Musicavatar — Plan de implementación

**Asignatura:** Ingeniería de Software II · **Fase:** De la arquitectura al código ejecutable (Unidad 5) · **Lenguaje:** Python

## Estrategia de construcción: abajo hacia arriba (bottom-up)

1. Primero construimos las clases base (`Track`, `MusicDatabase`) y las funciones que extraen metadatos de archivos locales.
2. Después integramos reproducción y un controlador de estados emocionales con pruebas de datos y validación de errores.
3. Finalmente conectamos estos módulos a la interfaz PySide6 y verificamos el flujo completo importación → reproducción → avatar.

## Caso de uso principal: Reproducir una canción local

**Actor:** Usuario. **Precondición:** La aplicación se abre correctamente y el archivo musical existe en el disco.

1. Selecciona una carpeta o un archivo compatible.
2. El lector de metadatos valida ruta/extensión y extrae título, artista, álbum, género, duración y portada.
3. `MusicDatabase.add_track()` registra una canción evitando duplicados.
4. El usuario hace doble clic sobre la canción en la biblioteca o en la cola.
5. `AudioPlayer.load_and_play()` intenta reproducirla y reporta errores; el controlador actualiza información, barra de progreso y escena del avatar.
6. `get_track_mood()` utiliza el género o la categoría manual para determinar el ambiente visual.

**Validaciones:** carpeta vacía, archivo ausente, extensión no aceptada, duplicados, listas sin nombre y posible fallo del motor de audio.

## Distribución sugerida para un equipo de 3 integrantes

| Integrante (asignar nombre real) | Módulo / responsabilidad | Entregable verificable |
|---|---|---|
| Integrante 1 (coordinación) | `models.py`, `database.py`, `queue_logic.py`, `track_table.py`, `player.py`, integración de `ui.py` | Reproducción local, interfaz, base de datos y commit |
| Integrante 2 | `genres.py`, `moods.py`, `tests/test_genres.py`, `tests/test_moods.py` | Etiquetas de género múltiples, clasificación de emoción y pruebas; commit independiente |
| Integrante 3 | `utils.py`, `tests/test_utils.py` y documentación de escenarios | Funciones de formato, pruebas y evidencia; commit independiente |

Si son **2 integrantes**, unir las responsabilidades 2 y 3, sin alterar los nombres de módulos. Todas las contribuciones deben revisarse y probarse antes del `git push`.

## Entregables y criterios de verificación

- Código ejecutable y caso de uso completo (abrir música → reproducir → actualizar avatar).
- Diagrama UML propuesto en `docs/DIAGRAMA_CLASES.md`, actualizado a las clases realmente implementadas.
- Matriz de correspondencia en `docs/MATRIZ_TRAZABILIDAD.md`.
- Tres capturas **reales**: dos casos exitosos y un error controlado (`docs/PRUEBAS.md`).
- Repositorio compartido, con al menos un commit **real** por integrante, según la consigna.

> **Nota de trazabilidad:** la consigna pide utilizar el diagrama original de la Unidad 4. Como aquí no se recibió ese diagrama específico, se incluye una propuesta correspondiente a la implementación. Antes de entregar, verificar con el diseño real de la Unidad 4 y documentar cambios, si existen.

## Ampliación V0.2 (correcciones funcionales)

- Se separó `Inicio` de `Biblioteca`: avatar, top 3 de canciones y top 3 listas con accesos directos.
- Se agregó `PlaybackQueue` para mantener cola, historial, aleatorio y repetición sin depender de la vista de la tabla.
- Se implementaron filtros y vista eficiente Qt mediante `TrackModel` y `TrackFilter`, con selección múltiple y acciones por lotes.
- SQLite recibió columnas `play_count` por migración aditiva, conservando datos anteriores.
- Se incorporaron iconos vectoriales, fondos por emoción con mosaicos estáticos y divisores de tamaño ajustable.

**Estado de pruebas:** el núcleo se comprueba con `py -m unittest discover -s tests -v`. Las pruebas de interfaz y audio en Windows deben registrarse con capturas reales; las comprobaciones de modelo Qt incluidas se ejecutan cuando PySide6 está instalado.
