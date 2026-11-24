# Guía para los commits de los compañeros

## Objetivo

Que **cada integrante participe con cambios verificables**, sin tocar simultáneamente `ui.py`, `database.py` ni `player.py`, que son las partes más propensas a provocar conflictos.

### Contribución pequeña A — Géneros y emociones

**Archivo:** `musicavatar/moods.py`.

1. Añadir al diccionario `GENRE_RULES` 2 o 3 géneros musicales que falten.
2. Verificar el resultado con `py -m unittest discover -s tests -v`.
3. Añadir una prueba de clasificación a `tests/test_moods.py`.
4. Commit personal sugerido: `git add musicavatar/moods.py tests/test_moods.py` y `git commit -m "Ampliar generos y validar estados emocionales"`.

### Contribución pequeña B — Formato y pruebas

**Archivos:** `musicavatar/utils.py` y `tests/test_utils.py`.

1. Mejorar las pruebas de `format_time()` para valores de 0, minutos, horas y entradas negativas.
2. Añadir una función auxiliar pequeña sin dependencia de la interfaz, si el equipo identifica una necesidad real.
3. Confirmar que las pruebas pasan.
4. Commit personal sugerido: `git add musicavatar/utils.py tests/test_utils.py` y `git commit -m "Mejorar utilidades y pruebas de formato"`.

### Flujo seguro

Antes de modificar: `git pull`. Edita **solo tu módulo**, ejecuta las pruebas, haz `git add`, `git commit` y `git push`. Si el push se rechaza por cambios remotos, coordina con el equipo antes de resolver el conflicto. No subas `data/musicavatar.db`, portadas extraídas ni tu música personal.

**No se han generado commits en nombre de los compañeros:** deben realizarlos desde sus propias cuentas.
