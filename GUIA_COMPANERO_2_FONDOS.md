# Paquete 2: Personalización del escenario del avatar

**Responsable:** compañero/a encargado/a del módulo de Fondos. Trabaja en su **propia cuenta de GitHub**. El responsable principal debe haber subido el **puente de integración** antes de comenzar.

## Objetivo

Dentro de **Personalizar**, al desplazarse hacia abajo, añadir **Fondo del escenario**. La herramienta permite seleccionar una imagen PNG/JPG/WEBP, elegir **Rellenar** o **Ajustar**, regular el oscurecimiento y restaurar el fondo original. El escenario se conserva al cerrar y abrir Musicavatar, sin alterar las prendas ni las emociones.

## Archivos incluidos

- `musicavatar/contrib/avatar_backgrounds.py` — selección, vista previa, controles, almacenamiento local y conexión con el avatar.
- `musicavatar/contrib/background_rules.py` — validación de extensiones, archivos, tamaños y límites de ajustes.
- `tests/test_contrib_backgrounds.py` — cinco pruebas de validación y opciones.

No debes tocar `ui.py`, `main.py`, `avatar.py` ni `database.py`. El puente ya proporciona el método de dibujado de fondo.

## Cómo subir tu aporte (VS Code / PowerShell)

1. Acepta la invitación como colaborador/a del proyecto en GitHub.
2. Abre VS Code y clona el repositorio (no uses la carpeta de otro integrante):

```powershell
git clone https://github.com/Ranelty/MUSICAVATAR.git
cd MUSICAVATAR
git switch main
git pull --ff-only origin main
git switch -c feature/fondos-avatar
```

3. Extrae este ZIP y copia su contenido a la raíz de `MUSICAVATAR/` respetando las carpetas.
4. Instala dependencias si no las tienes: `py -m pip install -r requirements.txt`.
5. Ejecuta:

```powershell
py -m unittest discover -s tests -p "test_contrib_backgrounds.py" -v
py main.py
```

6. En Musicavatar abre **Personalizar**, baja hasta **Fondo del escenario**, elige una imagen y prueba Rellenar/Ajustar y el oscurecimiento. Cierra y reabre el programa para verificar persistencia; finalmente usa Restaurar.
7. Revisa y sube **tus propios archivos y commit**:

```powershell
git status
git add musicavatar/contrib/avatar_backgrounds.py musicavatar/contrib/background_rules.py tests/test_contrib_backgrounds.py GUIA_COMPANERO_2_FONDOS.md
git commit -m "Agregar fondos de avatar personalizables"
git push -u origin feature/fondos-avatar
```

8. En GitHub abre **Compare & pull request** hacia `main` y pide al responsable que lo fusione.

> **No ejecutes `git push --force`.** Si la rama ya existe, elige un nombre propio, por ejemplo `feature/fondos-avatar-angel`.

## Seguridad y rendimiento

- Una imagen de usuario se convierte a PNG reducido, almacenado en `data/avatar_backgrounds/scene.png`.
- Esta carpeta es local, queda excluida del Git por `.gitignore` y no se mezcla con los archivos musicales.
- Se aceptan imágenes hasta 15 MB; se comprueban extensiones y lectura del contenido.
- No añade bibliotecas adicionales, no usa Internet y no cambia el funcionamiento del reproductor.

## Evidencias para la tarea

Captura de **Personalizar** con imagen elegida, prueba al reiniciar, resultado de los tests y captura de tu commit/PR en GitHub.
