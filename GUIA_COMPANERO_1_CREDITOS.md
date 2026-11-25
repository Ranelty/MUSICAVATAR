# Paquete 1: Créditos y Acerca de Musicavatar

**Responsable:** compañero/a encargado/a del módulo de Créditos. Trabaja en su **propia cuenta de GitHub**. El responsable principal debe haber subido el **puente de integración** antes de comenzar.

## Objetivo

Insertar un botón **Créditos** debajo de Configuraciones, que abre una ventana modal con los tres integrantes (nombres proporcionados por el equipo), descripción, versión y tecnologías utilizadas.

## Archivos incluidos

- `musicavatar/contrib/credits.py` — botón, cuadro de diálogo e integración con la barra lateral.
- `musicavatar/contrib/credits_info.py` — información del equipo separada de la interfaz.
- `tests/test_contrib_credits.py` — tres pruebas de los datos mostrados.

No debes tocar `ui.py`, `main.py`, `avatar.py` ni `database.py`.

## Cómo subir tu aporte (VS Code / PowerShell)

1. En GitHub, el responsable principal te agrega como colaborador: **Settings → Collaborators → Add people**; acepta la invitación.
2. Abre VS Code y clona el proyecto en una carpeta de tu computadora distinta de la del responsable:

```powershell
git clone https://github.com/Ranelty/MUSICAVATAR.git
cd MUSICAVATAR
git switch main
git pull --ff-only origin main
git switch -c feature/creditos
```

3. Extrae **este** ZIP y copia su contenido a la raíz de `MUSICAVATAR/`, respetando la estructura de carpetas. No copies otra versión completa del reproductor.
4. Instala dependencias si todavía no las tienes: `py -m pip install -r requirements.txt`.
5. Prueba el módulo:

```powershell
py -m unittest discover -s tests -p "test_contrib_credits.py" -v
py main.py
```

6. En la app abre **Créditos** desde la izquierda y comprueba que aparecen los tres nombres.
7. Revisa los archivos y crea **tu propio commit**:

```powershell
git status
git add musicavatar/contrib/credits.py musicavatar/contrib/credits_info.py tests/test_contrib_credits.py GUIA_COMPANERO_1_CREDITOS.md
git commit -m "Agregar creditos y ventana acerca de Musicavatar"
git push -u origin feature/creditos
```

8. En GitHub aparecerá **Compare & pull request**. Abre el PR hacia `main`, explica qué probaste y avisa al responsable para que lo revise y lo fusione.

> **No ejecutes `git push --force`.** El commit debe aparecer asociado a tu cuenta. Si una rama `feature/creditos` ya existe, crea otra con tu usuario, por ejemplo `feature/creditos-rafael`.

## Evidencias para la tarea

Captura de la ventana Créditos funcionando, de la ejecución de tus pruebas y de tu commit/PR propio en GitHub. Son evidencias complementarias a las capturas generales que pida el profesor.
