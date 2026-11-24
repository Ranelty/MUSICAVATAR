"""Inicio de Musicavatar. Ejecutar con: py main.py"""
import sys
from PySide6.QtWidgets import QApplication
from musicavatar.ui import MusicavatarWindow
from musicavatar.team_bridge import install_team_modules


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Musicavatar')
    app.setOrganizationName('Musicavatar')
    window = MusicavatarWindow()
    install_team_modules(window)
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
