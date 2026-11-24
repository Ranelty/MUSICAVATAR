"""Hoja de estilos de Musicavatar. El panel izquierdo siempre es oscuro."""
from .moods import MOODS

GLOBAL_QSS = '''
* { font-family: "Segoe UI", Arial; font-size: 12px; }
QMainWindow, QWidget#Root { background: #121017; color: #eae5f0; }
QWidget#Sidebar { background: #17141e; border-right: 1px solid #322a3b; }
QWidget#PlaylistCard { background: #26202f; border:1px solid #483751; border-radius:12px; }
QWidget#PlaylistCard:hover { background: #34283d; border:1px solid #936cb7; }
QWidget#HeroCard, QWidget#StatusCard { background: #25202d; border: 1px solid #3f3547; border-radius: 15px; }
QLabel { color: #ece6f3; background: transparent; }
QLabel#Brand { font-weight: 900; font-size: 23px; letter-spacing: 1px; color: #e5d4ff; }
QLabel#Heading { font-size: 18px; font-weight: 800; }
QLabel#SmallHeading { font-size: 13px; font-weight: 800; }
QLabel#Muted { font-size: 11px; color: #a69bac; }
QLabel#AccentHeading { font-size: 14px; font-weight: 800; color: #c2a0ff; }
QPushButton { background: #2c2634; color: #e7e0f1; border: 1px solid #463952; border-radius: 9px; padding: 8px 11px; font-weight: 650; }
QPushButton:hover { background: #3b3148; border-color: #71598b; }
QPushButton:pressed { background: #51405e; }
QPushButton:disabled { color: #807887; background: #25222a; }
QPushButton#NavButton { text-align: left; background: transparent; border: none; border-radius: 9px; padding: 10px 13px; color: #aaa0b5; font-size: 13px; }
QPushButton#NavButton:hover { background: #2c2536; color: #f3edfc; }
QPushButton#NavButton[active="true"] { background: #3d3150; color: #f2e5ff; border-left: 3px solid #b795ed; }
QPushButton#Primary { background: #b996ea; border: none; color: #1d132b; font-weight: 900; }
QPushButton#Primary:hover { background: #d4b8ff; }
QPushButton#Control { background: transparent; border: none; padding: 6px; min-width: 25px; min-height: 25px; }
QPushButton#Control:hover { background:#43314d; }
QPushButton#ToggleControl { background: #28222e; border: 1px solid #3a3044; padding: 5px; min-width: 25px; min-height: 25px; }
QPushButton#ToggleControl:checked { background: #71559a; border: 2px solid #ebc5ff; }
QPushButton#ToggleControl:hover { background:#604873; }
QWidget#PlayerBar { background:#211c29;border:1px solid #4a3a58;border-radius:13px; }
QSplitter::handle:vertical { background: #665477; min-height: 5px; max-height: 5px; margin: 0px; border: none; }
QSplitter::handle:horizontal { background: #544264; min-width: 5px; max-width: 5px; margin: 0px; border: none; }
QSplitter::handle:hover { background: #ba94ee; }

QPushButton#PlayButton { background: #bd9cee; border: none; color: #1d1627; border-radius: 23px; padding: 0px; }
QPushButton#PlayButton:hover { background: #ddc5ff; }
QLineEdit, QComboBox, QSpinBox { color: #ebe5f2; border-radius: 9px; border: 1px solid #43384d; background: #2b2532; padding: 8px; selection-background-color: #7c5ca6; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #ab89db; }
QComboBox QAbstractItemView { background: #292431; color: #eee3f6; selection-background-color: #4d3f5f; }
QListWidget, QTableView { background: transparent; color: #e7e1e9; border: none; outline: none; gridline-color: #393142; alternate-background-color: #231e29; }
QListWidget::item { border-radius: 6px; padding: 7px 5px; }
QListWidget::item:selected, QTableView::item:selected { background: #4b3a60; color: #fff; }
QHeaderView::section { background: #27212e; color: #ae9bb9; padding: 8px; border: none; border-bottom: 1px solid #44394d; font-size: 11px; font-weight: 700; }
QTableView::item { padding: 5px 7px; border-bottom: 1px solid #302937; }
QSlider::groove:horizontal { height: 5px; background: #4b4252; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #b593e7; border-radius: 2px; }
QSlider::handle:horizontal { width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; background: #eee0ff; }
QCheckBox { color: #eee4f7; spacing: 10px; padding: 5px; }
QCheckBox::indicator { width: 17px; height: 17px; }
QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { width: 8px; background: transparent; }
QScrollBar::handle:vertical { background: #51445e; border-radius: 4px; min-height: 18px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QMenu { background: #2a2332; color: #eee5f3; border: 1px solid #5d4e69; padding: 5px; }
QMenu::item { padding: 7px 20px; }
QMenu::item:selected { background: #504061; }
QToolTip { color: white; background: #302739; border: 1px solid #5e4d6f; }
'''


def panel_styles(mood: str) -> tuple[str,str]:
    item = MOODS.get(mood, MOODS['neutral'])
    tint, accent = item['tint'], item['accent']
    # Fondo plano, sin ondas ni animación constante: bajo consumo.
    return (f'QWidget#MainPanel {{ background: {tint}; }}',
            f'QWidget#RightPanel {{ background: {tint}; border-left: 1px solid #3a3341; }}')
