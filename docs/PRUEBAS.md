# Musicavatar — Guía de pruebas y tres evidencias requeridas

La consigna solicita **tres capturas de la aplicación ejecutándose**: **dos casos exitosos** y **un caso de manejo de error**. Las siguientes son pruebas propuestas, **no evidencias ya realizadas**. Las capturas deben obtenerse del programa funcionando en Windows.

## Evidencia 1: importación y reproducción (éxito)

1. Abrir Musicavatar con `py main.py`.
2. Seleccionar **Importar carpeta**, abrir la carpeta `demo/` y comprobar que aparezcan las pistas.
3. Reproducir **Amanecer en píxeles**.
4. **Resultado esperado:** se escucha el audio, aparece el título y se actualiza el indicador de progreso y la emoción.
5. Guardar la captura como `evidencia_01_reproduccion.png`.

## Evidencia 2: contribuciones del equipo (éxito)

1. Tras fusionar los Pull Requests, abrir **Créditos** y comprobar los tres nombres. Tomar una captura del diálogo.
2. En **Personalizar**, elegir una imagen local compatible como fondo del avatar, probar **Rellenar / Ajustar**, cerrar y reabrir Musicavatar, y verificar que la selección persiste.
3. Guardar al menos la captura del escenario personalizado como `evidencia_02_fondo_avatar.png`. La captura de Créditos puede incluirse como **evidencia complementaria**.

## Evidencia 3: validación de error (controlado)

1. Importar una pista local desde `demo/`.
2. Cerrar Musicavatar y cambiar temporalmente el nombre de **ese archivo de prueba** desde el Explorador de Windows.
3. Volver a abrir la aplicación y solicitar reproducir la pista registrada.
4. **Resultado esperado:** Musicavatar informa que el archivo no existe y no se cierra inesperadamente.
5. Guardar la captura como `evidencia_03_archivo_inexistente.png`.
6. Restaurar el nombre del archivo de prueba para que vuelva a funcionar.

## Tabla de resultados para completar después de ejecutarlas

| Caso | Resultado esperado | Resultado observado | Estado | Evidencia |
|---|---|---|---|---|
| Importar y reproducir | Audio, metadatos y avatar actualizados | Pendiente | Pendiente | `evidencia_01_reproduccion.png` |
| Fondo personalizado y créditos | Se aplica fondo y están visibles los créditos | Pendiente | Pendiente | `evidencia_02_fondo_avatar.png` + opcional Créditos |
| Archivo inexistente | Advertencia sin cierre inesperado | Pendiente | Pendiente | `evidencia_03_archivo_inexistente.png` |

## Verificación adicional de los módulos

- Christofer: los nombres corresponden a la lista del equipo, la ventana cierra bien y la reproducción continúa.
- Ángel Mario: PNG/JPG/WEBP válidos, imágenes inválidas rechazadas, ajuste, oscurecimiento, restauración y persistencia de la imagen guardada.
- Rafael: imports, reproducción, pausa, cola, filtros y migraciones de SQLite.

**No generar capturas ficticias:** usar exclusivamente evidencias reales del programa durante la prueba.
