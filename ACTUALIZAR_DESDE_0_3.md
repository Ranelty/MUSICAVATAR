# Musicavatar v0.4 — actualización desde v0.3

## Antes de reemplazar archivos

1. Cierra Musicavatar y cierra cualquier editor de audio que mantenga tus canciones abiertas.
2. Haz una copia de seguridad de **toda** la carpeta `data/` de tu proyecto, incluyendo `musicavatar.db` y las carátulas guardadas. No sustituyas esa carpeta por la del ZIP.
3. Extrae el ZIP. Copia **el contenido de `Musicavatar/`** encima de tu carpeta actual `MUSICAVATAR/`. Acepta reemplazar el código anterior.
4. No borres `.git/`, `data/`, tus propios archivos de música ni tus playlists.
5. Abre Terminal de VS Code en la carpeta del proyecto y ejecuta:

```powershell
py -m pip install -r requirements.txt
py main.py
```

`numpy` y `imageio-ffmpeg` se agregaron para generar un espectro real, sin depender de que VLC exponga el audio PCM. Si están instalados, el analizador solo se usa al **activar** la opción.

## ¿Qué cambió?

- Nueva sección «Configuraciones» en la barra izquierda, junto al resto de secciones.
- Color neutral del fondo configurable, por defecto morado. Los colores emocionales siguen siendo automáticos.
- Visualizador **desactivado por defecto**; 32 o 64 barras y color a elección. Usa audio real del archivo, con análisis FFT en un hilo separado, y consulta la posición de reproducción de VLC/Qt para sincronizar. La primera carga de una canción puede requerir algunos segundos para calcular el espectro, y el consumo de CPU aumenta ligeramente mientras se analiza. Las barras aparecen en una franja discreta debajo de la zona principal.
- Editor: **Título** modifica la etiqueta musical; la opción «Renombrar también el archivo de audio» modifica además su nombre físico en Windows. Está desmarcada por defecto. El nombre del archivo no se puede sustituir si ya existe otro con el mismo nombre; se conservan ID, playlists y favoritos en la base de datos al renombrar correctamente.

## Prueba recomendada

1. Abre Configuraciones: deja apagadas las barras y verifica que la interfaz esté normal.
2. Reproduce uno de los MP3 de `demo/`, activa 32 barras y comprueba que se mueven; luego elige 64.
3. Cambia el color de las barras y el color principal del fondo. Reinicia la aplicación para revisar persistencia.
4. Haz copia de un MP3, impórtalo y cambia su título desde el menú contextual. Comprueba el título en la biblioteca y con otro lector de etiquetas. Repite marcando la casilla de renombrar archivo.
5. Desactiva las barras y verifica que se ocultan.

**Limitaciones:** El visualizador no escucha Spotify, micrófonos ni audio del resto del sistema, solo el archivo local reproducido. El espectro se precalcula en segundo plano y se sincroniza por posición. Si cambias muchas veces de canción el análisis previo se cancela. Para una primera carga puede permanecer quieto mientras se analiza. No se ha probado la interfaz en el Windows de tu PC.
