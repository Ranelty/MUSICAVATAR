# Actualización Musicavatar v0.4 → v0.5

## Qué cambia

La actualización añade capas intercambiables para el avatar pixel art. La música, playlists, estadísticas, preferencias y motor de reproducción de v0.4 no se reemplazan. Las barras de audio permanecen opcionales y desactivadas si así las dejaste.

**Nuevas opciones en la barra izquierda → Personalizar:**

- Presentación: Masculino, Femenino, Neutro (estilos visuales sutiles).
- Cabello: Corto, Despeinado, Largo; múltiples colores.
- Prenda superior: Camiseta, Camisa, Sudadera; colores intercambiables.
- Pantalón: Negro, Mezclilla o Beige.
- Zapatos: Tenis blancos, Tenis rojos o Botas oscuras.
- Tono de piel: Claro, Medio u Oscuro.
- Accesorios: Auriculares, Gorra, Moño o Ninguno.

Los ajustes se guardan automáticamente en `data/musicavatar.db` y se ven en el avatar principal y en la vista previa. El avatar conserva sus estados emocionales y su escenario.

## Pasos para instalar (Windows + Visual Studio Code)

1. **Cierra Musicavatar.**
2. Haz una copia de seguridad de tu carpeta `data` completa (en particular `data/musicavatar.db`).
3. Descomprime `Musicavatar_v0.5.zip`. Abre la carpeta `Musicavatar` que contiene `main.py`.
4. Copia esos archivos y carpetas **encima** de tu proyecto actual, sin borrar `.git`, `data` ni tu música local.
5. Abre tu proyecto en VS Code y ejecuta `py main.py`.

No necesitas instalar bibliotecas nuevas: la personalización utiliza PySide6, que ya está en `requirements.txt`.

## Comprobaciones recomendadas

1. En «Personalizar», selecciona cabello largo, piel oscura y tenis rojos; mira el avatar principal.
2. Reproduce música alegre/triste y verifica que las expresiones siguen funcionando.
3. Cierra y vuelve a abrir Musicavatar: las selecciones deben permanecer.
4. Cierra Personalizar con la X: regresa la cola de reproducción.
5. Verifica que «Biblioteca», «Listas» y reproducción se mantienen intactas.

## Nota

La carga de una fotografía/imagen de fondo **todavía no está implementada**: la reservamos para una siguiente actualización. Para mantener el consumo bajo, el personaje usa solo figuras de píxeles, sin texturas externas pesadas. No hemos modificado el visualizador, así que puedes seguir dejándolo apagado.
