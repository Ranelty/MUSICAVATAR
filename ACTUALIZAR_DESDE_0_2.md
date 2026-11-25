# Actualizar de Musicavatar 0.2 a 0.3 SIN perder tu biblioteca

1. **Cierra Musicavatar** y asegúrate de que no esté reproduciendo música.
2. Haz un **respaldo completo de `MUSICAVATAR/data/`**, especialmente de `musicavatar.db`, `covers/` y cualquier arte personalizado. Si ya cambiaste etiquetas de audios originales, respalda también esos archivos importantes.
3. Descomprime `Musicavatar_v0.3.zip`. Abre la carpeta **`Musicavatar/` dentro del ZIP**.
4. Copia **el contenido** de esa carpeta (no la carpeta externa) en tu repositorio actual `MUSICAVATAR`, sobreescribiendo el código, los tests y la documentación.
5. **No reemplaces ni elimines tu carpeta `data/`, ni `.git/`.** El ZIP contiene `data/.gitkeep`, no tus datos privados. Tu repositorio GitHub no se desvinculará.
6. En VS Code, desde la carpeta que contiene `main.py`, ejecuta:

```powershell
py main.py
```

7. La base de datos se migrará agregando `playlists.cover` y `mood_totals`. No se eliminan canciones, favoritos ni listas. Se reinicia **una vez** el tamaño guardado del separador horizontal para evitar la franja gruesa de 0.2; puedes volver a arrastrarlo.
8. Si al iniciar hay un error, cierra el programa y restaura la carpeta `data/` que respaldaste. Conserva el texto de la terminal para diagnosticarlo.

## Cómo probar primero

- Abre **Biblioteca** y comprueba el recorte centrado de las portadas.
- Muestra **Cola** y revisa las miniaturas pequeñas por canción.
- Abre **Listas**, crea una vacía, pulsa «Después agrego» y luego «+ Canciones» para completar la lista. Pasa el cursor sobre otra tarjeta para ver reproducción, aleatorio y «Portada…».
- En **Biblioteca**, haz clic derecho en una sola canción de **prueba** y elige «Editar metadatos del archivo original…». Haz una copia de ese MP3 antes de editarlo.
- Pon música y abre **Inicio** para revisar el avatar más grande, portadas de rankings y tiempo por emoción.


