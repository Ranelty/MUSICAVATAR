"""Punto de integración opcional para contribuciones de integrantes.

El núcleo de Musicavatar sigue funcionando si alguno de los módulos no existe.
Cada integrante añade únicamente su archivo en musicavatar/contrib/.
"""
from __future__ import annotations
import importlib
import importlib.util
import logging

MODULES = (
    'musicavatar.contrib.credits',
    'musicavatar.contrib.avatar_backgrounds',
)


def install_team_modules(window) -> list[str]:
    """Instala los módulos disponibles y devuelve sus nombres (para pruebas)."""
    loaded: list[str] = []
    for module_name in MODULES:
        if importlib.util.find_spec(module_name) is None:
            continue
        try:
            module = importlib.import_module(module_name)
            module.install(window)
        except Exception:
            logging.exception('No se pudo cargar el módulo %s', module_name)
            try:
                window.statusBar().showMessage('Error al cargar módulo: ' + module_name, 12000)
            except Exception:
                pass
        else:
            loaded.append(module_name)
    return loaded
