# Pruebas funcionales y capturas para la entrega

## Prueba exitosa 1 — Importar y reproducir

1. Abre Musicavatar con `py main.py`.
2. Haz clic en **Importar carpeta** y elige `demo/`.
3. Verifica que aparezcan dos pistas, los títulos, el artista *Musicavatar Demo*, el género y las carátulas.
4. Haz doble clic en **Amanecer en píxeles**.
5. **Resultado esperado:** se oye audio, el progreso cambia y el avatar muestra *Alegre* con fondo cálido.
6. **Evidencia:** captura real de la interfaz mientras reproduce la canción.

## Prueba exitosa 2 — Modificación manual

1. Haz doble clic en **Lluvia en la ventana**.
2. Confirma que aparece el ánimo *Melancólico* y un tono azul/gris suave.
3. En **Cambiar emoción**, selecciona *Tranquilo*.
4. **Resultado esperado:** la app actualiza el ánimo y el color, sin que deje de sonar la canción. La selección se conserva tras reiniciar.
5. **Evidencia:** segunda captura real de reproducción o personalización.

## Prueba de error — Archivo inexistente

1. Importa uno de los archivos de `demo/`.
2. Cierra la aplicación y **cambia temporalmente de nombre** ese archivo desde el explorador de Windows.
3. Abre Musicavatar e intenta reproducir la pista que sigue registrada.
4. **Resultado esperado:** mensaje **«Archivo no encontrado»**, sin cierre inesperado. 
5. **Evidencia:** captura real con la advertencia en pantalla.
6. **Restaurar:** devuelve al archivo su nombre original.

## Otras pruebas recomendadas

- Repetir una importación: no se duplica la canción.
- Seleccionar una carpeta sin audio: mensaje «Sin canciones».
- Crear una lista vacía o con nombre ya existente: se rechaza de manera controlada.
- Marcar favoritos, filtrar por búsqueda, cambiar temas, pausar y reanudar.
- Probar MP3, FLAC y M4A locales: identificar archivos que fallen por codecs, sin confundirlos con los resultados de éxito.

**No adjuntamos capturas simuladas como si fueran la ejecución real:** las tres imágenes deben tomarse en la computadora del equipo al realizar estas pruebas.

## Pruebas nuevas de la versión 0.2

1. **Inicio distinto de Biblioteca:** al pulsar Inicio deben aparecer top 3 de pistas y listas; Biblioteca debe mostrar la tabla.
2. **Cola completa:** vacía la cola, pulsa **Reponer todas**; deben recuperarse todas las canciones sin reimportarlas. En Biblioteca, **Reproducir todo** debe sustituir la cola por todas las canciones visibles filtradas.
3. **Listas:** crea una lista, añade 3 canciones y haz doble clic en la segunda: la cola debe contener la segunda y la tercera, en ese orden.
4. **Selección múltiple:** Ctrl: selecciona pista 3, luego pista 1 y pista 5; clic derecho → Añadir a cola debe agregarlas en orden 3→1→5. Shift: selecciona rango 2–5 y agrégalo, debe quedar 2→3→4→5.
5. **Historial aleatorio:** enciende Aleatorio (resalte visible), reproduce 3 canciones y pulsa Anterior; debe volver a la última escuchada, no a la fila anterior de la cola.
6. **Emoción manual:** durante reproducción cambia varias veces el Combo de emoción; no debe dejar de responder la interfaz ni detenerse el audio.
7. **Varios géneros:** clic derecho → Editar géneros → escribe `Rock, Pop`; el filtro Rock y el filtro Pop deben mostrar esa canción.
8. **Tamaños:** arrastra el divisor horizontal (central/cola) y vertical (avatar/tabla), cierra Musicavatar, vuelve a abrirlo; deben conservarse los tamaños guardados.
9. **Iconos:** comprueba que los botones reproducir, pausa, siguiente, anterior, aleatorio, repetir y volumen son iconos vectoriales y no emojis dependientes de la fuente.

> Importante: estas son **pruebas manuales pendientes de ejecutar en el equipo con Windows**; no se presentan como evidencias ya obtenidas.
