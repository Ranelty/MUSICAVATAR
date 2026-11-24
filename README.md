# 🎵 Musicavatar

**Tu música, tu mundo.** Reproductor de audio **local y sin streaming**, construido con Python, PySide6, SQLite, Mutagen y LibVLC (con alternativa Qt Multimedia). Incluye un avatar pixel art que reacciona al género o al estado emocional asignado manualmente, sin requerir IA ni internet.

## Funciones de Musicavatar 0.3

- Importa **archivos o carpetas** de música local (también admite arrastrar archivos o carpetas a la ventana).
- Intenta reproducir MP3, FLAC, WAV, OGG, M4A, AAC, OPUS y WMA. *El formato admitido realmente depende del motor y códecs disponibles*. 
- Controles vectoriales (sin emojis) de reproducción, pausa, canción anterior/siguiente, volumen, avance, repetición y aleatorio, con estados activos bien visibles. El aleatorio respeta el historial real y no repite hasta acabar la cola, salvo al activar repetición.
- Lee metadatos **título, artista, álbum, género, duración y carátulas** incrustadas; si no hay portada busca `cover.jpg` o `folder.jpg` junto a la música.
- Guarda biblioteca, favoritos, listas, emoción manual, **estadísticas de reproducciones** y personalización del avatar en una **base de datos local SQLite**. Se conservan las bases antiguas al actualizar.
- **Inicio propio:** avatar en grande, top 3 canciones y top 3 listas con portadas, y tiempo total acumulado por emoción. **Biblioteca:** tabla filtrable por género(s), artista, álbum y emoción. **Listas:** tarjetas con portada y botones flotantes de reproducir/aleatorio; pulsar una tarjeta abre sus canciones y el doble clic reproduce la elegida y las siguientes en orden.
- **Cola con portadas:** miniaturas cuadradas centradas para cada pista, con caché de imágenes para evitar sobrecarga.
- **Editor real de metadatos:** clic derecho en **una sola canción** → «Editar metadatos del archivo original…». Modifica título, artista, álbum, géneros y portada incrustada en formatos compatibles. **Modifica el archivo original:** respalda tu música antes. Las ediciones colectivas de géneros hechas desde «Editar géneros» modifican la biblioteca SQLite, no los archivos.
- **Listas con portadas:** al crear una se abre un selector de canciones filtrable con la opción «Después agrego»; también se puede asignar una miniatura propia con el botón al pasar el cursor sobre su tarjeta.
- **Géneros normalizados:** Rock/rock se unifican y un selector sugiere nombres similares; géneros evidentes en los títulos (por ejemplo, «Lo-Fi» u «OST») pueden sugerirse al importar si faltan etiquetas. No es reconocimiento real del sonido ni adivina artistas.
- **Cola recuperable:** «Reproducir todo» para todas las visibles y «Reponer todas» para la biblioteca completa.
- **Selección múltiple:** Ctrl para clics en orden de selección y Shift para rango en orden visual. Clic derecho aplica acciones (cola, favorito, emoción, géneros y playlist) a todas las seleccionadas.
- **Paneles redimensionables:** arrastra el divisor vertical avatar/lista y el divisor lateral central/cola. Se guardan los tamaños.
- Una cola a la derecha; clic en **Personalizar** para sustituirla temporalmente por el editor del avatar.
- Un avatar de pixel art, dibujado con código: duerme cuando no hay reproducción, cambia su mundo según el ánimo y tiene una escena especial de lluvia para escuchar música triste durante 30 minutos consecutivos. El fondo principal utiliza un **degradado arriba y abajo, fundido a oscuro en el centro, con pequeños píxeles estáticos**, y la barra izquierda no cambia.
- Música de demostración **original**, creada para verificar la aplicación sin usar pistas con copyright.

> **Si ya tienes la versión 0.2**, lee primero [`ACTUALIZAR_DESDE_0_2.md`](ACTUALIZAR_DESDE_0_2.md) y respalda `data/musicavatar.db` antes de reemplazar archivos.

> **No es Spotify:** Musicavatar no descarga música ni consulta catálogos externos. Nunca subas tu biblioteca musical personal al repositorio.

## 1. Abrir en Visual Studio Code (Windows)

1. Abre la carpeta de tu repositorio local **MUSICAVATAR** en VS Code.
2. Copia en **la raíz de esa carpeta** los archivos de esta entrega, de modo que `main.py` quede junto a `requirements.txt` (no dentro de una segunda carpeta `Musicavatar`).
3. En la terminal de VS Code, crea opcionalmente un entorno virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell impide activar el entorno, puedes omitir la activación y usar directamente `.\.venv\Scripts\python.exe` en los comandos.

4. Instala las dependencias:

```powershell
py -m pip install -r requirements.txt
```

Si creaste y activaste el entorno virtual, usa `python -m pip install -r requirements.txt` para instalarlas dentro de ese entorno. Si no usas entorno virtual, el comando `py -m pip` funciona con tu instalación principal de Python.

5. Instala **VLC Media Player de 64 bits**, si no lo tienes: https://www.videolan.org/vlc/ . `python-vlc` es solo el controlador; VLC proporciona `libvlc.dll`. Si VLC no está disponible, Musicavatar intenta usar Qt Multimedia.
6. Ejecuta:

```powershell
py main.py
```

Si estás dentro de un entorno activado, ejecuta `python main.py` para usar el intérprete correcto. VS Code permite seleccionar el intérprete con **Python: Select Interpreter**.

**Versión de Python**: el programa está escrito pensando en Python 3.10+ y PySide6 6.x. Si usas Python 3.15, la instalación de dependencias no garantiza por sí misma que todo funcione: ejecútalo y comunica cualquier error.

## 2. Primer uso

1. Presiona **＋ Importar carpeta** o **＋ Añadir archivos**.
2. Selecciona tu carpeta de música; prueba primero con la carpeta `demo/`, que incluye dos canciones originales etiquetadas.
3. Entra en **Biblioteca** para ver la tabla. Haz doble clic sobre una canción: comenzará esa pista **y las siguientes visibles** en la cola, en el mismo orden. En **Listas**, mantiene el orden de las pistas de la lista.
   También puedes utilizar **Reproducir todo**, **Modo aleatorio** o **Reponer todas** después de vaciar la cola.
4. Observa la portada, el artista, el progreso, la emoción y el fondo cambiar.
5. En el panel **Estado del avatar**, cambia la emoción a **Alegre** o **Melancólico** si el género del archivo no corresponde a lo que transmite.
6. Pulsa **Personalizar** en la barra izquierda para cambiar cabello, vestimenta y accesorio; vuelve a pulsarlo o usa **✕** para ver la cola.
7. Usa clic derecho sobre una canción o varias seleccionadas con Ctrl/Shift para reproducir, añadir a cola, favoritos o listas, asignar emociones y organizar géneros. Solo con una canción se ofrece **«Editar metadatos del archivo original…»** (requiere permiso de escritura y respaldo del audio).
8. Los rankings del **Inicio** registran **inicios de reproducción** (no minutos). Abajo aparecen los **tiempos totales por emoción**, que se suman mientras la música esté reproduciéndose.
9. En **Listas**, crea una lista (aparecerá un selector con filtros y «Después agrego»), pasa el cursor sobre las tarjetas para reproducir/aleatorio/cambiar portada, o abre la tarjeta para ver sus pistas. Usa los **separadores arrastrables** para ampliar la tabla o la cola y reducir la zona del avatar.

**Atajos:** `Espacio` para pausa/reproducir (salvo al escribir en la barra de búsqueda) y `Ctrl+O` para elegir archivos.

## 3. ¿Dónde están mis datos?

La base de datos se crea al iniciar en:

```text
MUSICAVATAR/data/musicavatar.db
```

Puedes abrirla con **DB Browser for SQLite**: https://sqlitebrowser.org/ . Las portadas extraídas se guardan en `data/covers/` y las portadas de listas en `data/playlist_covers/` y el proyecto las excluye de Git con `.gitignore`. La base de datos no almacena audios, solo **rutas absolutas** a los archivos de tu equipo. Si mueves una canción, tendrás que quitarla de la biblioteca y volver a importarla.

## 4. Estructura del código

```text
MUSICAVATAR/
├── main.py                       # Ejecuta la aplicación
├── requirements.txt              # Bibliotecas Python
├── musicavatar/
│   ├── ui.py                      # Ventana y eventos (controlador)
│   ├── avatar.py                  # Escenas y animación pixel art
│   ├── player.py                  # VLC / Qt Multimedia
│   ├── database.py                # Persistencia SQLite
│   ├── models.py                  # Clase Track
│   ├── metadata.py                # Lectura de tags y carátulas
│   ├── metadata_edit.py           # Escritura de etiquetas originales
│   ├── dialogs.py                 # Editores y selector de canciones
│   ├── playlist_cards.py          # Tarjetas de listas con portadas
│   ├── splitters.py               # Divisores de tamaño acotado
│   ├── moods.py                   # Reglas de emoción por género
│   ├── genres.py                  # Varias etiquetas de género / edición
│   ├── queue_logic.py             # Cola, aleatorio e historial real
│   ├── track_table.py             # Modelo Qt y filtros rápidos
│   ├── backdrop.py                # Gradiente estático de emoción
│   ├── vector_icons.py            # Iconos de controles sin emojis
│   ├── styles.py                  # Colores y apariencia de ventana
│   └── utils.py                   # Funciones auxiliares
├── demo/                          # Dos audios de prueba originales
├── tests/                         # Pruebas automáticas sin interfaz
├── docs/                          # UML, matriz, pruebas y colaboración
├── PLAN_IMPLEMENTACION.md
├── ACTUALIZAR_DESDE_0_1.md
├── CHANGELOG.md
├── data/                          # SQLite/caratulas (no subir a Git)
└── .gitignore
```

## 5. Pruebas para la entrega

Ejecuta:

```powershell
py -m unittest discover -s tests -v
```

Después toma **capturas reales de tu propia computadora**: (1) reproducción de la pista alegre, (2) reproducción de la pista melancólica o personalización y (3) error controlado, por ejemplo mover uno de los audios después de importarlo y pulsar reproducir. Encontrarás el guion en [`docs/PRUEBAS.md`](docs/PRUEBAS.md).

**Documentación para el profesor:** [`PLAN_IMPLEMENTACION.md`](PLAN_IMPLEMENTACION.md), [`docs/DIAGRAMA_CLASES.md`](docs/DIAGRAMA_CLASES.md), [`docs/MATRIZ_TRAZABILIDAD.md`](docs/MATRIZ_TRAZABILIDAD.md) y [`docs/COLABORACION.md`](docs/COLABORACION.md).

## 6. Subir el avance a GitHub

Dentro de la carpeta local del repositorio (donde ya vinculaste `origin`):

```powershell
git add .
git commit -m "Actualizar Musicavatar v0.3: listas, portadas y metadatos"
git push
```

Cada integrante hará su **propio commit** con una mejora independiente. Para reducir conflictos, el equipo puede dividirse los archivos `moods.py`, `utils.py` y/o sus pruebas; lee `docs/COLABORACION.md`. En la entrega **no damos por hechos** commits que todavía no se hayan realizado.

## Limitaciones conocidas de esta versión

- La detección de emociones **no analiza las ondas sonoras** ni las letras: interpreta el **género registrado en los metadatos**. El usuario puede corregirlo manualmente.
- Puede haber pistas sin portada, artista o género. Musicavatar solo infiere géneros cuando hay pistas textuales inequívocas (como «Lo-Fi»), y nunca garantiza reconocer automáticamente el género correcto sin una etiqueta o servicio externo.
- No existe sincronización con Spotify ni identificación online de canciones. La edición del archivo original se ha comprobado con MP3 de prueba; la compatibilidad de escritura de otros formatos debe verificarse con copias antes de editar música valiosa.
- El personaje fuera de la aplicación tipo **Shimeji** queda como mejora opcional futura.
- La importación de bibliotecas muy grandes todavía podría ocupar el hilo principal temporalmente; la **navegación entre secciones y el filtrado** ya utilizan un modelo Qt eficiente.
- **No se ha ejecutado la interfaz ni el sonido en este entorno de creación** porque no hay PySide6 disponible. Deben verificarse en Windows. Los tests automáticos del núcleo sí fueron ejecutados.
- Las escenas se dibujan con primitivas pixel art para priorizar bajo consumo; el arte puede ampliarse más adelante.

## Novedades v0.4 — Configuraciones

La sección **Configuraciones** (barra izquierda) permite elegir un color base para el fondo neutral; no cambia el aspecto del avatar ni la paleta automática de otros estados de ánimo. También permite **activar o desactivar** un espectro real, seleccionar **32 o 64 barras** y personalizar su color. El visualizador está apagado por defecto.

El analizador usa `numpy` y `imageio-ffmpeg` para decodificar audio PCM temporalmente y calcular bandas mediante FFT. Corre en segundo plano y solo retiene bandas compactas, no la canción decodificada. Debes instalar las dependencias nuevas con `py -m pip install -r requirements.txt` después de actualizar. La carga inicial del espectro puede tardar un poco; no depende del volumen del sistema ni recoge audio de otras aplicaciones.

### Título musical vs nombre de archivo

En la opción **Editar metadatos del archivo original…** el campo Título cambia la etiqueta musical dentro del archivo. Si también quieres que cambie el nombre del archivo de Windows, marca la nueva opción **Renombrar también el archivo de audio**, desmarcada inicialmente. Haz una copia de seguridad antes de probar esta función. La biblioteca seguirá apuntando al archivo renombrado y conservará sus playlists, favoritos y estadísticas.

Consulta `ACTUALIZAR_DESDE_0_3.md` antes de reemplazar la v0.3.

## Personalización del avatar (v0.5)

Ve a **Personalizar** en la barra izquierda. Se abrirá el panel derecho, sustituyendo temporalmente la cola, y podrás elegir: presentación del personaje, estilo/color de cabello, tipo/color de prenda superior, pantalón, zapatos, tono de piel y accesorio. Cada categoría tiene 3 opciones de prueba (algunas paletas tienen más colores). Los cambios se reflejan al instante en el avatar y su vista previa y se guardan en SQLite para futuras sesiones.

El avatar permanece en su mundo pixel art y **continúa reaccionando al estado emocional de la música**. El fondo del escenario todavía es el de prueba; la opción de usar una imagen propia se reserva para una actualización posterior. La pantalla de configuración del visualizador no ha cambiado: las barras siguen siendo opcionales.

**Actualización desde v0.4:** lee `ACTUALIZAR_DESDE_0_4.md` y respalda `data/musicavatar.db` antes de reemplazar los archivos. No hace falta agregar nuevas bibliotecas ni importar nuevamente tus canciones.
