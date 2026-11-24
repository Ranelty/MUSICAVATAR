# Pasar de Musicavatar 0.1 a 0.2 sin perder la biblioteca

1. **Cierra Musicavatar** si está abierto.
2. En la carpeta actual `MUSICAVATAR`, copia como respaldo **`data/musicavatar.db`** a otra ubicación temporal. Esta base contiene canciones importadas, favoritos, listas y personalización. Puedes respaldar también `data/covers` si tienes portadas extraídas.
3. Descarga y descomprime esta versión. En el ZIP verás una carpeta `Musicavatar`.
4. **Copia el contenido de esa carpeta** dentro de tu proyecto existente `MUSICAVATAR`, es decir, `main.py`, `musicavatar/`, `tests/`, `docs/`, etc., y acepta reemplazar los archivos del programa.
5. **No borres ni reemplaces** tu carpeta personal `data/` existente; el ZIP solo incluye `data/.gitkeep` y no una base de datos. Si por accidente desaparece tu biblioteca, recupera el respaldo del paso 2.
6. No borres `.git/`: es la carpeta que vincula tu proyecto a GitHub. El ZIP no incluye `.git/`.
7. Abre VS Code en la raíz del proyecto, con `main.py` al mismo nivel que `requirements.txt`, y ejecuta `py main.py`.
8. Musicavatar detecta y añade automáticamente las columnas nuevas (`play_count`) a la base anterior. **No elimina tus canciones ni playlists.**

## Para subir tus cambios

```powershell
git status
git add .
git commit -m "Mejorar reproductor Musicavatar v0.2"
git push
```

No subas canciones privadas ni la base SQLite local. Cada compañero debe hacer su propio commit con su módulo.
