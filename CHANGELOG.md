# Musicavatar — historial de cambios

## Versión 0.3 — Playlists visuales y edición local

- Separador horizontal de anchura fija muy fina (5 px) y reinicio del tamaño guardado anteriormente; no debería volver a verse una columna gris ancha.
- Recorte **centrado** de portadas rectangulares; miniaturas con caché en cada fila de la cola, Inicio y listas.
- **Listas** empieza en una galería de tarjetas con carátulas. Al pasar el cursor aparecen reproducir, aleatorio y cambiar imagen; al pulsar se abre la tabla de canciones.
- Creación de listas mediante ventana modal con selección por casillas, filtro de género, artista y orden A-Z, y botón «Después agrego».
- Nuevo editor modal de metadatos para **una canción**, que escribe título, artista, álbum, géneros y carátula en el archivo original mediante Mutagen. No modifica el audio codificado, pero sí los metadatos; respaldar antes.
- Catálogo de géneros con normalización de variantes y sugerencias de cercanía. Algunos nombres de título/álbum como Lo-Fi u OST permiten una inferencia conservadora. No hay clasificación automática de audio ni consulta a servicios externos.
- **Inicio:** avatar más grande, top 3 con portadas y totales de tiempo acumulado por emoción.
- Fondo de emoción con gradientes arriba y abajo y centro oscuro, sin animación gráfica pesada.
- SQLite migra sumando la columna de carátula de playlists y la tabla de tiempos por emoción.
- 48 pruebas del núcleo pasadas; 4 tests de interfaz omitidos porque PySide6 no está instalado en este entorno. La GUI debe validarse en Windows.



## Versión 0.2 — Mejoras del reproductor

- **Inicio separado de Biblioteca:** muestra al avatar y el top 3 de canciones/listas más escuchadas. Los botones «Reproducir todo» y «Modo aleatorio» en Inicio actúan sobre toda la biblioteca. Doble clic en un ranking inicia esa canción/lista.
- **Biblioteca, Favoritos y Listas:** vista de tabla más eficiente basada en un modelo Qt con filtros por género, artista, álbum, emoción y texto. La vista de Listas mantiene el orden de la playlist.
- **Cola reconstruible:** «Reproducir todo» añade la selección visible completa; «Reponer todas» recupera la biblioteca tras vaciar la cola. Al dar doble clic a una canción en la biblioteca o lista, se reproducirá ella y las siguientes filas visibles en ese orden.
- **Iconos limpios:** reproducción, pausa, anterior, siguiente, aleatorio, repetir y volumen en vectores SVG locales, sin fuentes de emoji. Aleatorio y repetición tienen estado visual claramente activo.
- **Historial de reproducción:** en modo aleatorio, «Anterior» regresa a la canción realmente escuchada antes, no a la anterior de la tabla. Sin repetición, el aleatorio termina después de recorrer todas las canciones de la cola.
- **Etiquetas de género múltiples:** Musicavatar lee todas las etiquetas de género compatibles, permite editar manualmente varios géneros separados por comas y filtrarlos individualmente.
- **Acciones por lotes:** Ctrl selecciona canciones en orden de clic; Shift selecciona un rango en orden visible. Clic derecho permite reproducir, agregar a cola, favoritos, lista, asignar emoción, editar géneros o quitar de la biblioteca. Las inserciones múltiples en playlist usan una sola transacción SQLite.
- **Emociones más estables:** cambiar una emoción no reconstruye la biblioteca. El fondo cambia de color con pequeños mosaicos estáticos (sin ondas ni animación del fondo); la barra lateral izquierda permanece oscura.
- **Tamaños ajustables:** divisores entre avatar/biblioteca y panel central/cola mediante QSplitter. El tamaño se recuerda entre sesiones.
- **Migración compatible:** columnas `play_count` agregadas a tablas antiguas sin borrar las canciones, playlists ni las emociones de Musicavatar 0.1.
- **Avatar sin rediseñar:** se mantienen las animaciones y el mundo pixel art del prototipo anterior; solo se permite que ocupe un espacio menor al mover el divisor.

## Límites y próximos pasos

La detección emocional se basa en géneros escritos en el archivo o asignación manual. No «escucha» ni clasifica automáticamente el sonido. No se ha cambiado la ilustración de prueba del avatar ni se ha implementado el modo Shimeji. La reproducción real, los codecs y la visualización en Windows deben verificarse en la computadora del equipo.

## v0.4 — Editor de títulos, configuraciones y espectro real

- Configuraciones en la barra lateral izquierda con color del tema neutral personalizable.
- Visualizador apagado por defecto, 32/64 barras, color configurable y preferencias guardadas en SQLite.
- Espectro de frecuencia del audio local mediante FFmpeg y FFT de NumPy, en hilo separado. Almacena cada fotograma como 64 bytes; sin carga de análisis si está apagado.
- Editor de etiquetas: explicita la diferencia entre título de metadatos y nombre físico del archivo; casilla opcional para renombrar el audio sin eliminar playlists o favoritos.
- Pruebas v0.4 de metadatos y migración de rutas.

## v0.5 — Avatar modular (personalización inicial)

- Nuevo personaje chibi pixel art de capas procedurales, inspirado en las proporciones de la referencia aportada.
- Personalización de corte y color de cabello, prenda superior y su color, pantalones, zapatos, tono de piel, presentación y accesorios.
- Panel derecho desplazable con vista previa y cambios reflejados en el avatar principal en tiempo real.
- Ajustes persistentes en SQLite con retrocompatibilidad para el color del pelo, ropa y accesorios de v0.4.
- El panel vuelve a la cola de reproducción cuando se cierra, sin alterar la reproducción ni las estadísticas.
- Animaciones de estado musical conservadas; se mantiene el motor de audio y el visualizador tal como estaban en v0.4.
- 12 pruebas nuevas (9 de lógica y 3 opcionales de Qt). Próxima mejora reservada: imagen propia para el escenario del avatar.
