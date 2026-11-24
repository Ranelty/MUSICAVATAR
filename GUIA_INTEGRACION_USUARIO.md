# Musicavatar: puente de integración (solo responsable principal)

Este paquete se aplica **primero** sobre el repositorio `Ranelty/MUSICAVATAR`, que ya tiene Musicavatar v0.5. Permite añadir los módulos de los compañeros por separado y sin editar el mismo archivo.

## Qué contiene

- `main.py`: intenta cargar los módulos presentes después de crear la ventana.
- `musicavatar/team_bridge.py`: detecta módulos opcionales; la app sigue funcionando aunque todavía no estén.
- `musicavatar/avatar.py`: añade un fondo opcional detrás del personaje, manteniendo los sprites y escenarios originales cuando no se configura un fondo.
- `musicavatar/contrib/__init__.py`: carpeta donde los compañeros añadirán sus módulos.

No reemplaza `ui.py`, `database.py`, `player.py`, `data/` ni tu música.

## Pasos del responsable principal (en VS Code)

1. **Cierra Musicavatar**. Respalda `data/musicavatar.db` y tu carpeta `data/`.
2. Comprueba que tu repositorio ya está al día: `git switch main` y `git pull --ff-only origin main`.
3. Extrae este ZIP. Copia sus archivos **dentro de la raíz `MUSICAVATAR/`** y combina las carpetas; `main.py` debe quedar en la misma carpeta que `requirements.txt`.
4. Revisa `git status` para verificar que **solo** cambian el archivo de inicio, el del avatar y los nuevos archivos del puente (más la guía si la copiaste).
5. Ejecuta `py -m unittest discover -s tests -p "test_team_bridge.py" -v` y `py main.py`. El programa debe abrir aunque aún no tenga Créditos ni Fondo personalizado.
6. Haz tu propio commit:

```powershell
git add main.py musicavatar/avatar.py musicavatar/team_bridge.py musicavatar/contrib/__init__.py tests/test_team_bridge.py GUIA_INTEGRACION_USUARIO.md
git commit -m "Preparar integracion de aportaciones del equipo"
git push origin main
```

7. Pasa a cada compañero su ZIP individual **después** de que el puente se haya subido a `main`.

## Cómo quedan integradas las aportaciones

- El compañero 1 sube `musicavatar/contrib/credits.py` y `credits_info.py`, además de su prueba.
- El compañero 2 sube `musicavatar/contrib/avatar_backgrounds.py` y `background_rules.py`, además de su prueba.
- Cada uno trabaja en su rama `feature/...` y abre un **Pull Request** hacia `main`; tú revisas y fusionas.
- Después de cada fusión, ejecuta `git pull --ff-only origin main` y abre `py main.py`. El botón **Créditos** aparecerá en la barra lateral y los **Fondos** en el panel **Personalizar** sin editar nada más.

## Prueba final y seguridad

- Créditos: comprueba nombres y cierre de la ventana.
- Fondos: selecciona una imagen de prueba, usa Rellenar/Ajustar, cambia oscurecimiento, reinicia la app, y comprueba que se conserva. Pulsa Restaurar para recuperar el escenario original.
- Las imágenes personales se almacenan en `data/avatar_backgrounds/` y **no se suben a Git** por el `.gitignore` existente.
- Si Git muestra un conflicto, **no uses `git push --force`**. Revisa archivos y coordina antes de mezclar cambios.

> El puente se ha comprobado mediante pruebas de Python, pero las interacciones de PySide6 deben probarse en Windows con tu instalación.
