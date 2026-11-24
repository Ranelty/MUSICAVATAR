"""Musicavatar 0.5: música local, edición real de tags y biblioteca de playlists."""
from __future__ import annotations
import base64
import random
import shutil
import hashlib
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QSize, QItemSelectionModel, QByteArray
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QComboBox, QListWidget,
    QListWidgetItem, QHeaderView, QMessageBox, QSlider, QFrame, QStackedWidget,
    QInputDialog, QMenu, QSizePolicy, QAbstractItemView, QProgressDialog, QSplitter,
    QScrollArea, QDialog, QProgressBar, QCheckBox, QSpinBox, QColorDialog,
)
from .avatar import AvatarCanvas
from .avatar_parts import (
    HAIR_COLORS, OUTFIT_COLORS, HAIR_STYLES, TOP_STYLES, PANTS,
    SHOES, SKIN_TONES, PRESENTATIONS, ACCESSORIES,
)
from .backdrop import AmbientPanel
from .spectrum import SpectrumWidget
from .database import MusicDatabase
from .genres import split_genres, normalize_genres, infer_genre_from_words
from .metadata import SUPPORTED_EXTENSIONS, scan_paths, read_track
from .moods import MOODS, MoodSession, get_track_mood
from .models import Track
from .player import AudioPlayer
from .queue_logic import PlaybackQueue
from .styles import GLOBAL_QSS
from .track_table import TrackModel, TrackFilter, OrderedTrackView
from .utils import format_time
from .vector_icons import icon
from .playlist_cards import PlaylistCard
from .splitters import CompactSplitter
from .dialogs import GenreDialog, TrackMetadataDialog, AddSongsDialog, exec_blurred
from .metadata_edit import write_file_tags, WRITABLE_EXTENSIONS

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'


def label(text: str, name: str | None = None, wrap: bool = False) -> QLabel:
    widget = QLabel(text)
    if name:
        widget.setObjectName(name)
    widget.setWordWrap(wrap)
    return widget


def push(text: str, style: str | None = None, width: int | None = None) -> QPushButton:
    button = QPushButton(text)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    if style:
        button.setObjectName(style)
    if width:
        button.setFixedWidth(width)
    return button


def vbox(widget: QWidget, margin=0, gap=10) -> QVBoxLayout:
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(margin,margin,margin,margin)
    layout.setSpacing(gap)
    return layout


_COVER_CACHE: dict[tuple[str,int], QPixmap] = {}

def track_pixmap(track: Track | None, size=54) -> QPixmap:
    """Portada en caché, evitando leer una imagen enorme en cada repintado."""
    cover = track.cover if track else ''
    key = (cover, size)
    if key in _COVER_CACHE:
        return _COVER_CACHE[key]
    pm = QPixmap(size, size)
    if cover and Path(cover).is_file():
        loaded = QPixmap(cover)
        if not loaded.isNull():
            scaled = loaded.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                   Qt.TransformationMode.SmoothTransformation)
            # Centrar el recorte, NO mostrar solo la esquina izquierda superior.
            left = max(0, (scaled.width()-size)//2)
            top = max(0, (scaled.height()-size)//2)
            pm = scaled.copy(left,top,size,size)
            if len(_COVER_CACHE) > 300:
                _COVER_CACHE.clear()
            _COVER_CACHE[key] = pm
            return pm
    pm.fill(QColor('#403253'))
    p = QPainter(pm)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor('#7d609a'))
    p.drawEllipse(size//5,size//5,size*3//5,size*3//5)
    p.setBrush(QColor('#cbb4e6'))
    p.drawEllipse(size*2//5,size*2//5,size//5,size//5)
    p.end()
    _COVER_CACHE[key] = pm
    return pm


class MusicavatarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = MusicDatabase(DATA_DIR / 'musicavatar.db')
        self.player = AudioPlayer(self)
        self.session = MoodSession()
        self.tracks: dict[int,Track] = {}
        self.playback = PlaybackQueue()
        self.current_id: int | None = None
        self.current_tab = 'Inicio'
        self.active_playlist: int | None = None
        self.shuffle = False
        self.repeat = False
        self._seeking = False
        self._position_seconds = 0.0
        self._last_stage = -1
        self._last_mood = ''
        self._mood_pending: dict[str,float] = {}
        self._mood_flush_ticks = 0
        self._rendered_queue_ids: list[int] = []
        self._last_highlighted_index: int | None = None
        self._build_ui()
        self._connect_player()
        self.setStyleSheet(GLOBAL_QSS)
        self._load_settings()
        self.refresh_library(reset_queue=True)
        self._navigate('Inicio')
        self._refresh_mood()
        self.setWindowTitle('Musicavatar — tu música, tu mundo')
        self.setMinimumSize(1120, 720)
        self.resize(1360, 820)
        self.setAcceptDrops(True)
        self.setWindowIcon(QIcon(track_pixmap(None, 64)))
        self.statusBar().setStyleSheet('background:#19151e;color:#c9bcca;border-top:1px solid #332b39;')
        self.statusBar().showMessage(f'Musicavatar listo · Motor: {self.player.backend or "no disponible"}')
        if not self.player.backend:
            QTimer.singleShot(900, lambda: QMessageBox.warning(self, 'Motor de audio',
                'No se encontró un motor de audio utilizable. Instala VLC de 64 bits. '
                'La biblioteca seguirá funcionando.'))

    @property
    def queue(self) -> list[int]:
        return self.playback.items

    def _build_ui(self):
        root = QWidget()
        root.setObjectName('Root')
        self.setCentralWidget(root)
        root_l = QHBoxLayout(root)
        root_l.setContentsMargins(0,0,0,0)
        root_l.setSpacing(0)
        self._build_sidebar(root_l)
        self.horizontal_splitter = CompactSplitter(Qt.Orientation.Horizontal)
        self.horizontal_splitter.setHandleWidth(5)
        self.horizontal_splitter.setOpaqueResize(False)
        self.horizontal_splitter.setChildrenCollapsible(False)
        root_l.addWidget(self.horizontal_splitter,1)
        self._build_main()
        self._build_right()
        self.horizontal_splitter.setStretchFactor(0, 4)
        self.horizontal_splitter.setStretchFactor(1, 2)
        self.horizontal_splitter.setSizes([835,360])

    def _build_sidebar(self, root):
        sidebar = QWidget()
        sidebar.setObjectName('Sidebar')
        sidebar.setFixedWidth(205)
        layout = vbox(sidebar,21,12)
        layout.addWidget(label('♫  Musicavatar','Brand'))
        layout.addWidget(label('TU MÚSICA · TU MUNDO','Muted'))
        layout.addSpacing(23)
        self.nav_buttons = {}
        for symbol,name in [('⌂','Inicio'),('▤','Biblioteca'),('♥','Favoritos'),('☷','Listas'),('✦','Personalizar'),('⚙','Configuraciones')]:
            btn = push(f' {symbol}   {name}', 'NavButton')
            btn.setProperty('active', name == 'Inicio')
            btn.clicked.connect(lambda checked=False, tab=name: self._navigate(tab))
            layout.addWidget(btn)
            self.nav_buttons[name] = btn
        layout.addSpacing(19)
        layout.addWidget(label('COLECCIÓN','Muted'))
        folder = push('＋  Importar carpeta')
        folder.clicked.connect(self.import_folder)
        layout.addWidget(folder)
        files = push('＋  Añadir archivos')
        files.clicked.connect(self.import_files)
        layout.addWidget(files)
        layout.addStretch()
        layout.addWidget(label('✧  Un mundo en cada canción','Muted',True))
        layout.addWidget(label('Versión 0.5 · Música local','Muted'))
        root.addWidget(sidebar)

    def _build_main(self):
        self.main_panel = AmbientPanel('center')
        self.main_panel.setObjectName('MainPanel')
        self.main_panel.setMinimumWidth(605)
        layout = vbox(self.main_panel,0,13)
        layout.setContentsMargins(22,20,22,18)
        top = QHBoxLayout()
        heading = QVBoxLayout()
        heading.setSpacing(4)
        heading.addWidget(label('Tu rincón musical','Heading'))
        heading.addWidget(label('Un compañero para cada emoción','Muted'))
        top.addLayout(heading)
        top.addStretch()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Buscar canción, artista, álbum o género...')
        self.search.setMinimumWidth(180)
        self.search.setMaximumWidth(330)
        self.search.textChanged.connect(self._on_search_changed)
        top.addWidget(self.search)
        layout.addLayout(top)

        self.vertical_splitter = CompactSplitter(Qt.Orientation.Vertical)
        self.vertical_splitter.setHandleWidth(5)
        self.vertical_splitter.setChildrenCollapsible(False)
        self._build_avatar_area()
        self.lower_stack = QStackedWidget()
        self._build_home_page()
        self._build_library_page()
        self._build_playlists_overview()
        self._build_settings_page()
        self.vertical_splitter.addWidget(self.lower_stack)
        self.vertical_splitter.setStretchFactor(0,3)
        self.vertical_splitter.setStretchFactor(1,4)
        self.vertical_splitter.setSizes([425,250])
        layout.addWidget(self.vertical_splitter,1)
        self.spectrum = SpectrumWidget(self.main_panel)
        layout.addWidget(self.spectrum)
        self._build_player_bar(layout)
        self.horizontal_splitter.addWidget(self.main_panel)

    def _build_avatar_area(self):
        area = QWidget()
        area_l = QHBoxLayout(area)
        area_l.setContentsMargins(0,0,0,0)
        area_l.setSpacing(12)
        hero = QWidget()
        self.hero_card = hero
        hero.setObjectName('HeroCard')
        hero_l = vbox(hero,11,5)
        heading = QHBoxLayout()
        heading.addWidget(label('MI PEQUEÑO MUNDO','Muted'))
        heading.addStretch()
        heading.addWidget(label('PIXEL LIVE','Muted'))
        hero_l.addLayout(heading)
        self.avatar = AvatarCanvas()
        self.avatar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        hero_l.addWidget(self.avatar,1,Qt.AlignmentFlag.AlignCenter)
        self.avatar_caption = label('Un momento para descansar…','Muted')
        self.avatar_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_l.addWidget(self.avatar_caption)
        area_l.addWidget(hero,3)

        status = QWidget()
        self.status_card = status
        status.setObjectName('StatusCard')
        status.setMinimumWidth(190)
        status_l = vbox(status,14,8)
        status_l.addWidget(label('ESTADO DEL AVATAR','Muted'))
        self.mood_icon = label('☾')
        self.mood_icon.setStyleSheet('font-size:28px;color:#b99de9;')
        status_l.addWidget(self.mood_icon)
        self.mood_title = label('Dormido','Heading')
        status_l.addWidget(self.mood_title)
        self.mood_description = label('Esperando tu próxima canción.','Muted',True)
        status_l.addWidget(self.mood_description)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        status_l.addWidget(sep)
        status_l.addWidget(label('TIEMPO EN ESTE ÁNIMO','Muted'))
        self.mood_time = label('0:00','SmallHeading')
        status_l.addWidget(self.mood_time)
        status_l.addWidget(label('CAMBIAR EMOCIÓN','Muted'))
        self.mood_select = QComboBox()
        self.mood_select.addItem('Automático (género)','')
        for mood, data in MOODS.items():
            self.mood_select.addItem(data['label'],mood)
        self.mood_select.currentIndexChanged.connect(self.change_track_mood)
        status_l.addWidget(self.mood_select)
        status_l.addStretch()
        self.mood_explain = label('El avatar reacciona a tu música.','Muted',True)
        status_l.addWidget(self.mood_explain)
        area_l.addWidget(status,2)
        self.vertical_splitter.addWidget(area)

    def _build_home_page(self):
        home = QWidget()
        layout = vbox(home,0,10)
        row = QHBoxLayout()
        row.addWidget(label('Tu inicio','Heading'))
        row.addStretch()
        all_btn = push('Reproducir todo', 'Primary')
        all_btn.setToolTip('Reproduce toda tu biblioteca en orden')
        all_btn.clicked.connect(lambda: self.play_all(shuffle=False, source='home'))
        row.addWidget(all_btn)
        rand_btn = push('Modo aleatorio')
        rand_btn.setToolTip('Reproduce toda tu biblioteca en orden aleatorio')
        rand_btn.clicked.connect(lambda: self.play_all(shuffle=True, source='home'))
        row.addWidget(rand_btn)
        layout.addLayout(row)
        columns = QHBoxLayout()
        columns.setSpacing(12)
        col1 = QVBoxLayout()
        col1.addWidget(label('TOP 3 · CANCIONES MÁS ESCUCHADAS','Muted'))
        self.home_songs = QListWidget()
        self.home_songs.setIconSize(QSize(46,46))
        self.home_songs.itemDoubleClicked.connect(self._play_home_song)
        col1.addWidget(self.home_songs)
        col1.addWidget(label('Doble clic para escuchar','Muted'))
        col2 = QVBoxLayout()
        col2.addWidget(label('TOP 3 · LISTAS MÁS REPRODUCIDAS','Muted'))
        self.home_playlists = QListWidget()
        self.home_playlists.setIconSize(QSize(46,46))
        self.home_playlists.itemDoubleClicked.connect(self._play_home_playlist)
        col2.addWidget(self.home_playlists)
        col2.addWidget(label('Doble clic para reproducir lista','Muted'))
        columns.addLayout(col1,1)
        columns.addLayout(col2,1)
        layout.addLayout(columns,1)
        layout.addWidget(label('TUS EMOCIONES MÁS ESCUCHADAS · TIEMPO ACUMULADO','Muted'))
        self.home_mood_list = QListWidget()
        self.home_mood_list.setMaximumHeight(118)
        layout.addWidget(self.home_mood_list)
        self.lower_stack.addWidget(home)

    def _build_library_page(self):
        panel = QWidget()
        layout = vbox(panel,0,9)
        head = QHBoxLayout()
        self.back_to_playlists = push('← Listas')
        self.back_to_playlists.clicked.connect(self._show_playlist_overview)
        self.back_to_playlists.hide()
        head.addWidget(self.back_to_playlists)
        self.list_title = label('Biblioteca','Heading')
        head.addWidget(self.list_title)
        self.count_text = label('0 canciones','Muted')
        head.addWidget(self.count_text)
        head.addStretch()
        self.playlist_picker = QComboBox()
        self.playlist_picker.setMinimumWidth(135)
        self.playlist_picker.currentIndexChanged.connect(self._on_playlist_selection)
        head.addWidget(self.playlist_picker)
        self.add_playlist_songs_btn = push('＋ Canciones')
        self.add_playlist_songs_btn.clicked.connect(self._add_to_active_playlist)
        self.add_playlist_songs_btn.hide()
        head.addWidget(self.add_playlist_songs_btn)
        self.create_playlist_btn = push('＋ Lista')
        self.create_playlist_btn.clicked.connect(self.create_playlist)
        head.addWidget(self.create_playlist_btn)
        layout.addLayout(head)

        tools = QHBoxLayout()
        self.play_all_btn = push('Reproducir todo','Primary')
        self.play_all_btn.setToolTip('Poner todas las canciones visibles en la cola')
        self.play_all_btn.clicked.connect(lambda: self.play_all(shuffle=False))
        tools.addWidget(self.play_all_btn)
        self.shuffle_all_btn = push('Modo aleatorio')
        self.shuffle_all_btn.clicked.connect(lambda: self.play_all(shuffle=True))
        tools.addWidget(self.shuffle_all_btn)
        tools.addStretch()
        tools.addWidget(label('FILTRAR POR','Muted'))
        layout.addLayout(tools)

        filters = QHBoxLayout()
        filters.setSpacing(7)
        self.genre_filter = QComboBox()
        self.artist_filter = QComboBox()
        self.album_filter = QComboBox()
        self.mood_filter = QComboBox()
        for combo in (self.genre_filter,self.artist_filter,self.album_filter,self.mood_filter):
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            combo.currentIndexChanged.connect(self._apply_filters)
            filters.addWidget(combo)
        layout.addLayout(filters)

        self.track_model = TrackModel(self)
        self.proxy = TrackFilter(self)
        self.proxy.setSourceModel(self.track_model)
        self.table = OrderedTrackView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_track_menu)
        self.table.doubleClicked.connect(self._play_table_index)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(2,125)
        self.table.setColumnWidth(3,140)
        layout.addWidget(self.table,1)
        layout.addWidget(label('Ctrl: selección en orden de clics · Shift: rango en orden de filas · clic derecho: acciones múltiples','Muted',True))
        self.lower_stack.addWidget(panel)
        self._refresh_filter_options()

    def _build_player_bar(self, layout):
        frame = QWidget()
        frame.setObjectName('PlayerBar')
        bar = vbox(frame,12,10)
        top = QHBoxLayout()
        self.cover = QLabel()
        self.cover.setPixmap(track_pixmap(None,54))
        self.cover.setFixedSize(54,54)
        top.addWidget(self.cover)
        song = QVBoxLayout()
        song.setSpacing(3)
        self.now_title = label('Nada sonando','SmallHeading')
        self.now_artist = label('Importa tus canciones para comenzar','Muted')
        song.addWidget(self.now_title)
        song.addWidget(self.now_artist)
        top.addLayout(song,1)
        self.favorite_now = push('', 'Control')
        self.favorite_now.setIcon(icon('heart'))
        self.favorite_now.setIconSize(QSize(22,22))
        self.favorite_now.setToolTip('Añadir o quitar de favoritos')
        self.favorite_now.clicked.connect(self.favorite_current)
        top.addWidget(self.favorite_now)
        self.shuffle_btn = push('', 'ToggleControl')
        self.shuffle_btn.setIcon(icon('shuffle'))
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.setIconSize(QSize(22,22))
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        top.addWidget(self.shuffle_btn)
        self.prev_btn = push('', 'Control')
        self.prev_btn.setIcon(icon('previous'))
        self.prev_btn.setIconSize(QSize(24,24))
        self.prev_btn.setToolTip('Anterior (historial real si Aleatorio está activado)')
        self.prev_btn.clicked.connect(self.previous_track)
        top.addWidget(self.prev_btn)
        self.play_btn = push('', 'PlayButton')
        self.play_btn.setFixedSize(46,46)
        self.play_btn.setIcon(icon('play','#1d1627',26))
        self.play_btn.setIconSize(QSize(26,26))
        self.play_btn.setToolTip('Reproducir / pausar (espacio)')
        self.play_btn.clicked.connect(self.toggle_play)
        top.addWidget(self.play_btn)
        self.next_btn = push('', 'Control')
        self.next_btn.setIcon(icon('next'))
        self.next_btn.setIconSize(QSize(24,24))
        self.next_btn.setToolTip('Siguiente canción de la cola')
        self.next_btn.clicked.connect(self.next_track)
        top.addWidget(self.next_btn)
        self.repeat_btn = push('', 'ToggleControl')
        self.repeat_btn.setIcon(icon('repeat'))
        self.repeat_btn.setCheckable(True)
        self.repeat_btn.setIconSize(QSize(22,22))
        self.repeat_btn.clicked.connect(self.toggle_repeat)
        top.addWidget(self.repeat_btn)
        bar.addLayout(top)
        bottom = QHBoxLayout()
        self.elapsed = label('0:00','Muted')
        bottom.addWidget(self.elapsed)
        self.timeline = QSlider(Qt.Orientation.Horizontal)
        self.timeline.setRange(0,1000)
        self.timeline.sliderPressed.connect(self._seek_start)
        self.timeline.sliderReleased.connect(self._seek_end)
        bottom.addWidget(self.timeline,1)
        self.total = label('0:00','Muted')
        bottom.addWidget(self.total)
        bottom.addSpacing(11)
        speaker = QLabel()
        speaker.setPixmap(icon('volume').pixmap(19,19))
        bottom.addWidget(speaker)
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0,100)
        self.volume.setValue(74)
        self.volume.setMaximumWidth(77)
        self.volume.valueChanged.connect(self.player.set_volume)
        bottom.addWidget(self.volume)
        bar.addLayout(bottom)
        layout.addWidget(frame)
        self._refresh_mode_buttons()

    def _build_right(self):
        self.right_panel = AmbientPanel('right')
        self.right_panel.setObjectName('RightPanel')
        self.right_panel.setMinimumWidth(245)
        right = vbox(self.right_panel,15,12)
        header = QHBoxLayout()
        self.right_title = label('Cola de reproducción','Heading')
        header.addWidget(self.right_title)
        header.addStretch()
        self.right_close = push('', 'Control',32)
        self.right_close.setIcon(icon('close'))
        self.right_close.setIconSize(QSize(18,18))
        self.right_close.setToolTip('Cerrar personalización y volver a la cola')
        self.right_close.clicked.connect(self.show_queue)
        header.addWidget(self.right_close)
        self.right_close.hide()
        right.addLayout(header)
        self.right_stack = QStackedWidget()
        self._build_queue_panel()
        self._build_custom_panel()
        right.addWidget(self.right_stack,1)
        self.horizontal_splitter.addWidget(self.right_panel)

    def _build_queue_panel(self):
        panel = QWidget()
        layout = vbox(panel,0,11)
        layout.addWidget(label('A CONTINUACIÓN','Muted'))
        self.queue_list = QListWidget()
        self.queue_list.setSpacing(3)
        self.queue_list.setIconSize(QSize(44,44))
        self.queue_list.itemDoubleClicked.connect(self._play_queue_item)
        self.queue_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.queue_list.customContextMenuRequested.connect(self._queue_menu)
        layout.addWidget(self.queue_list,1)
        row = QHBoxLayout()
        clear = push('Vaciar cola')
        clear.clicked.connect(self.clear_queue)
        row.addWidget(clear)
        all_btn = push('Reponer todas','Primary')
        all_btn.setToolTip('Reconstruir la cola con la biblioteca completa')
        all_btn.clicked.connect(self.restore_full_queue)
        row.addWidget(all_btn)
        layout.addLayout(row)
        layout.addWidget(label('Doble clic para escuchar · arrastra los separadores para cambiar tamaños','Muted',True))
        self.right_stack.addWidget(panel)

    def _build_custom_panel(self):
        """Panel de personalización modular, desplazable y con vista previa.

        El avatar se mantiene a la izquierda como siempre; aquí editamos sus
        partes sin cargar imágenes ajenas ni alterar la cola de reproducción.
        """
        panel = QWidget()
        layout = vbox(panel,0,10)
        layout.addWidget(label('TU PERSONAJE, A TU GUSTO','Muted'))
        layout.addWidget(label('Cambia cada pieza y observa el resultado al instante.','Muted',True))
        self.avatar_preview = AvatarCanvas(preview=True)
        self.avatar_preview.setMinimumSize(120, 110)
        self.avatar_preview.setFixedHeight(174)
        layout.addWidget(self.avatar_preview)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        fields = vbox(inner,4,6)
        self._customizing_ready = False

        def option(label_text, items, attr):
            fields.addWidget(label(label_text, 'SmallHeading'))
            choice = QComboBox()
            for item in items:
                if isinstance(item, tuple):
                    choice.addItem(item[0],item[1])
                else:
                    choice.addItem(item,item)
            setattr(self,attr,choice)
            fields.addWidget(choice)
            choice.currentIndexChanged.connect(self._apply_customization)
            fields.addSpacing(3)

        option('Presentación del personaje',PRESENTATIONS,'presentation_choice')
        option('Estilo de cabello',HAIR_STYLES,'hair_style_choice')
        # Compatibilidad con los colores añadidos en v0.4.
        legacy_hairs = [('Castaño oscuro (v0.4)','#6d4b47'),
                        ('Azul (v0.4)','#608dbb'), ('Negro gris (v0.4)','#383846')]
        option('Color de cabello', HAIR_COLORS + tuple(legacy_hairs), 'hair_choice')
        option('Prenda superior',TOP_STYLES,'top_style_choice')
        option('Color de la ropa', OUTFIT_COLORS, 'outfit_choice')
        option('Pantalón',PANTS,'pants_choice')
        option('Zapatos',SHOES,'shoes_choice')
        option('Tono de piel',SKIN_TONES,'skin_choice')
        option('Accesorio',ACCESSORIES,'accessory_choice')
        fields.addWidget(label('Los cambios se guardan automáticamente en tu biblioteca local.','Muted',True))
        fields.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll,1)

        reset = push('Restablecer personaje')
        reset.clicked.connect(self._reset_customization)
        layout.addWidget(reset)
        self._customizing_ready = True
        self.right_stack.addWidget(panel)

    def _build_playlists_overview(self):
        overview = QWidget()
        overview_layout = vbox(overview,0,13)
        bar = QHBoxLayout()
        bar.addWidget(label('Tus listas de reproducción','Heading'))
        bar.addStretch()
        new_list = push('＋ Crear lista','Primary')
        new_list.clicked.connect(self.create_playlist)
        bar.addWidget(new_list)
        overview_layout.addLayout(bar)
        overview_layout.addWidget(label('Selecciona una tarjeta para abrir su contenido. Pasa el mouse para reproducirla.','Muted',True))
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        scroller.setFrameShape(QFrame.Shape.NoFrame)
        self.playlist_cards_container = QWidget()
        self.playlist_cards_grid = QGridLayout(self.playlist_cards_container)
        self.playlist_cards_grid.setContentsMargins(2,4,2,4)
        self.playlist_cards_grid.setSpacing(12)
        self.playlist_cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroller.setWidget(self.playlist_cards_container)
        overview_layout.addWidget(scroller,1)
        self.lower_stack.addWidget(overview)

    def _build_settings_page(self):
        """Preferencias ligeras y persistentes; ninguna requiere reiniciar."""
        page = QWidget()
        lay = vbox(page,8,13)
        lay.addWidget(label('Configuraciones', 'Heading'))
        lay.addWidget(label('Tema del fondo y visualizador de música', 'Muted'))
        lay.addSpacing(8)
        lay.addWidget(label('Color principal del fondo (en estado neutral)', 'SmallHeading'))
        self.theme_button = push('Elegir color del tema…')
        self.theme_button.clicked.connect(self._choose_theme_color)
        lay.addWidget(self.theme_button)
        reset_theme = push('Restaurar morado original')
        reset_theme.clicked.connect(lambda: self._apply_theme_color('#543362'))
        lay.addWidget(reset_theme)
        lay.addSpacing(10)
        lay.addWidget(label('Visualizador de frecuencias', 'SmallHeading'))
        self.spectrum_enabled = QCheckBox('Activar barras de audio (apagadas por defecto)')
        self.spectrum_enabled.toggled.connect(self._update_spectrum_options)
        lay.addWidget(self.spectrum_enabled)
        amount = QHBoxLayout()
        amount.addWidget(label('Cantidad de barras:'))
        self.spectrum_count = QComboBox()
        self.spectrum_count.addItem('32 barras', 32)
        self.spectrum_count.addItem('64 barras', 64)
        self.spectrum_count.currentIndexChanged.connect(self._update_spectrum_options)
        amount.addWidget(self.spectrum_count)
        lay.addLayout(amount)
        self.spectrum_color_button = push('Cambiar color de las barras…')
        self.spectrum_color_button.clicked.connect(self._choose_spectrum_color)
        lay.addWidget(self.spectrum_color_button)
        lay.addWidget(label('Las barras responden al audio real del archivo. El análisis se realiza en segundo plano; no capta sonidos de otras aplicaciones.', 'Muted', True))
        lay.addStretch()
        self.lower_stack.addWidget(page)

    def _choose_theme_color(self):
        old = QColor(self.db.get_setting('theme_color', '#543362'))
        color = QColorDialog.getColor(old, self, 'Color del tema de Musicavatar')
        if color.isValid():
            self._apply_theme_color(color.name())

    def _apply_theme_color(self, color):
        if not QColor(color).isValid():
            return
        self.db.set_setting('theme_color', color)
        self.theme_button.setText('Color del tema: ' + color.upper())
        self.main_panel.set_theme_color(color)
        self.right_panel.set_theme_color(color)

    def _choose_spectrum_color(self):
        color = QColorDialog.getColor(QColor(self.spectrum.color), self, 'Color del visualizador')
        if color.isValid():
            self.spectrum.color = color.name()
            self.spectrum_color_button.setText('Color de las barras: ' + color.name().upper())
            self.db.set_setting('spectrum_color', color.name())
            self.spectrum.update()

    def _update_spectrum_options(self, *args):
        enabled = self.spectrum_enabled.isChecked()
        self.spectrum.bars = self.spectrum_count.currentData() or 32
        self.spectrum.set_enabled(enabled)
        self.db.set_setting('spectrum_enabled', '1' if enabled else '0')
        self.db.set_setting('spectrum_count', str(self.spectrum.bars))
        if enabled and self.player.path:
            self.spectrum.set_track(self.player.path)
        self.spectrum.update()

    def _connect_player(self):
        self.player.position_changed.connect(self._update_position)
        self.player.state_changed.connect(self._state_changed)
        self.player.ended.connect(self._track_ended)
        self.player.error.connect(lambda message: QMessageBox.warning(self,'Reproducción',message))
        self.mood_tick = QTimer(self)
        self.mood_tick.setInterval(1000)
        self.mood_tick.timeout.connect(self._mood_tick)
        self.mood_tick.start()

    def _load_settings(self):
        try:
            self.volume.setValue(int(self.db.get_setting('volume','74')))
        except ValueError:
            self.volume.setValue(74)
        self.player.set_volume(self.volume.value())
        # Las claves antiguas siguen vigentes para no perder el avatar v0.4.
        for combo,key in self._avatar_settings():
            value = self.db.get_setting(key,'')
            index = combo.findData(value)
            if index >= 0:
                combo.blockSignals(True)
                combo.setCurrentIndex(index)
                combo.blockSignals(False)
        self._apply_customization()
        theme = self.db.get_setting('theme_color', '#543362')
        self._apply_theme_color(theme if QColor(theme).isValid() else '#543362')
        spectrum_color = self.db.get_setting('spectrum_color', '#bc93ea')
        self.spectrum.color = spectrum_color if QColor(spectrum_color).isValid() else '#bc93ea'
        self.spectrum_color_button.setText('Color de las barras: ' + self.spectrum.color.upper())
        index = self.spectrum_count.findData(int(self.db.get_setting('spectrum_count','32') or 32))
        self.spectrum_count.blockSignals(True)
        self.spectrum_count.setCurrentIndex(max(0,index))
        self.spectrum_count.blockSignals(False)
        self.spectrum_enabled.blockSignals(True)
        self.spectrum_enabled.setChecked(self.db.get_setting('spectrum_enabled','0') == '1')
        self.spectrum_enabled.blockSignals(False)
        self._update_spectrum_options()
        for splitter,key in ((self.horizontal_splitter,'split_h_v03'),(self.vertical_splitter,'split_v')):
            saved = self.db.get_setting(key)
            if saved:
                try:
                    splitter.restoreState(QByteArray(base64.b64decode(saved)))
                except (ValueError, TypeError):
                    pass

    def _avatar_settings(self):
        return (
            (self.presentation_choice,'presentation'),
            (self.hair_style_choice,'hair_style'),
            (self.hair_choice,'hair'),
            (self.top_style_choice,'top_style'),
            (self.outfit_choice,'outfit'),
            (self.pants_choice,'pants_style'),
            (self.shoes_choice,'shoes_style'),
            (self.skin_choice,'skin_tone'),
            (self.accessory_choice,'accessory'),
        )

    def _apply_customization(self, *unused):
        if not getattr(self, '_customizing_ready', False):
            return
        options = {key: combo.currentData() for combo,key in self._avatar_settings()}
        params = dict(hair=options['hair'], outfit=options['outfit'],
                      accessory=options['accessory'],
                      hair_style=options['hair_style'],
                      top_style=options['top_style'],
                      pants=options['pants_style'],
                      shoes=options['shoes_style'],
                      skin=options['skin_tone'],
                      presentation=options['presentation'])
        self.avatar.set_customization(**params)
        self.avatar_preview.set_customization(**params)
        # Cada cambio se persiste sin reemplazar la base de datos ni las listas.
        for key,value in options.items():
            if self.db.get_setting(key) != value:
                self.db.set_setting(key,value)

    def _reset_customization(self):
        for combo,key in self._avatar_settings():
            combo.blockSignals(True)
            # El primer valor es un ejemplo listo para usar, sin dependencias.
            combo.setCurrentIndex(0)
            combo.blockSignals(False)
        self._apply_customization()

    def _navigate(self, tab):
        if tab == 'Personalizar':
            self.show_queue() if self.right_stack.currentIndex() == 1 else self.show_customizer()
            return
        self.current_tab = tab
        for name,button in self.nav_buttons.items():
            if name == 'Personalizar':
                continue
            self._set_active_nav(button, name == tab)
        on_lists = tab == 'Listas'
        self.status_card.setVisible(tab not in ('Inicio','Configuraciones'))
        self.avatar.setMaximumHeight(465 if tab == 'Inicio' else 355)
        self.playlist_picker.setVisible(on_lists and self.lower_stack.currentIndex() == 1)
        self.create_playlist_btn.setVisible(on_lists and self.lower_stack.currentIndex() == 1)
        self.back_to_playlists.setVisible(on_lists and self.lower_stack.currentIndex() == 1)
        self.add_playlist_songs_btn.setVisible(on_lists and self.lower_stack.currentIndex() == 1)
        self.list_title.setText({'Biblioteca':'Biblioteca','Favoritos':'Tus favoritos','Listas':'Tus listas'}.get(tab,'Biblioteca'))
        if on_lists:
            self._show_playlist_overview()
        elif tab == 'Configuraciones':
            self.lower_stack.setCurrentIndex(3)
        else:
            self.lower_stack.setCurrentIndex(0 if tab == 'Inicio' else 1)
        self._update_table_context()
        if tab == 'Inicio':
            self._refresh_home()

    def _set_active_nav(self, button, enabled):
        button.setProperty('active',enabled)
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()

    def show_customizer(self):
        self.right_stack.setCurrentIndex(1)
        self.right_title.setText('Personalizar avatar')
        self.right_close.show()
        self._set_active_nav(self.nav_buttons['Personalizar'],True)

    def show_queue(self):
        self.right_stack.setCurrentIndex(0)
        self.right_title.setText('Cola de reproducción')
        self.right_close.hide()
        self._set_active_nav(self.nav_buttons['Personalizar'],False)

    def _refresh_home(self):
        self.home_songs.clear()
        songs = self.db.top_tracks()
        if not songs:
            self.home_songs.addItem('Tus canciones más escuchadas aparecerán aquí')
        for i,t in enumerate(songs,1):
            item = QListWidgetItem(f'{i}. {t.title}  ·  {t.artist}  ({t.play_count})')
            item.setIcon(QIcon(track_pixmap(t,46)))
            item.setSizeHint(QSize(200,55))
            item.setData(Qt.ItemDataRole.UserRole,t.id)
            self.home_songs.addItem(item)
        self.home_playlists.clear()
        playlists = self.db.top_playlists()
        if not playlists:
            self.home_playlists.addItem('Tus listas más reproducidas aparecerán aquí')
        for i,(pid,name,count) in enumerate(playlists,1):
            item = QListWidgetItem(f'{i}. {name}  ({count})')
            cover = self.db.get_playlist_cover(pid)
            ids = self.db.playlist_track_ids(pid)
            image = cover or (self.tracks[ids[0]].cover if ids and ids[0] in self.tracks else '')
            item.setIcon(QIcon(self._cover_from_path(image,46)))
            item.setSizeHint(QSize(200,55))
            item.setData(Qt.ItemDataRole.UserRole,pid)
            self.home_playlists.addItem(item)
        self.home_mood_list.clear()
        totals = self.db.mood_totals()
        for mood, pending in self._mood_pending.items():
            totals[mood] = totals.get(mood,0)+pending
        dominant = sorted(totals.items(),key=lambda item:item[1],reverse=True)[:4]
        if not dominant:
            self.home_mood_list.addItem('El tiempo por emoción aparecerá al escuchar música.')
        else:
            for mood, secs in dominant:
                if mood in MOODS:
                    self.home_mood_list.addItem(f"{MOODS[mood]['label']}   ·   {format_time(secs)} acumulados")

    def _cover_from_path(self,path,size=136):
        if not path or not Path(path).is_file():
            return track_pixmap(None,size)
        class Placeholder:
            cover = path
        return track_pixmap(Placeholder(),size)

    def _refresh_playlist_cards(self):
        grid = self.playlist_cards_grid
        while grid.count():
            child = grid.takeAt(0)
            widget = child.widget()
            if widget:
                widget.deleteLater()
        details = self.db.playlist_details()
        if not details:
            notice = label('Todavía no tienes listas. Usa «Crear lista» para comenzar.','Muted',True)
            grid.addWidget(notice,0,0)
            return
        for i,(pid,name,cover,plays,count) in enumerate(details):
            ids = self.db.playlist_track_ids(pid)
            first = self.tracks.get(ids[0]) if ids else None
            source = cover or (first.cover if first else '')
            card = PlaylistCard(pid,name,count,self._cover_from_path(source,138))
            card.opened.connect(self._open_playlist)
            card.play_requested.connect(self._play_playlist_card)
            card.cover_requested.connect(self._change_playlist_cover)
            grid.addWidget(card,i//3,i%3)

    def _show_playlist_overview(self):
        self.active_playlist = None
        self.lower_stack.setCurrentIndex(2)
        for button in (self.back_to_playlists,self.add_playlist_songs_btn,self.playlist_picker,self.create_playlist_btn):
            button.hide()
        self._refresh_playlist_cards()

    def _open_playlist(self,pid):
        if pid is None:
            return
        self.active_playlist = pid
        self.current_tab = 'Listas'
        for button in (self.back_to_playlists,self.add_playlist_songs_btn,self.playlist_picker,self.create_playlist_btn):
            button.show()
        self._populate_playlist_picker()
        idx = self.playlist_picker.findData(pid)
        if idx >= 0:
            self.playlist_picker.blockSignals(True)
            self.playlist_picker.setCurrentIndex(idx)
            self.playlist_picker.blockSignals(False)
        self.active_playlist = pid
        name = self.playlist_picker.currentText()
        self.list_title.setText(name or 'Lista')
        self.lower_stack.setCurrentIndex(1)
        self._update_table_context()

    def _play_playlist_card(self,pid,random_mode=False):
        self.start_playlist(pid,shuffle=random_mode)

    def _change_playlist_cover(self,pid):
        path,_ = QFileDialog.getOpenFileName(self,'Portada para la lista',str(Path.home()),
                                             'Imágenes (*.png *.jpg *.jpeg)')
        if not path:
            return
        try:
            if Path(path).stat().st_size > 6*1024*1024:
                raise ValueError('La imagen no debe pesar más de 6 MB.')
            image = QPixmap(path)
            if image.isNull():
                raise ValueError('El archivo no contiene una imagen válida.')
            folder = DATA_DIR/'playlist_covers'
            folder.mkdir(parents=True,exist_ok=True)
            destination = folder/f'{pid}_{hashlib.sha1(Path(path).read_bytes()).hexdigest()[:10]}{Path(path).suffix.lower()}'
            shutil.copy2(path,destination)
            self.db.set_playlist_cover(pid,str(destination))
            self._refresh_playlist_cards()
            if self.current_tab == 'Inicio':
                self._refresh_home()
        except (OSError,ValueError) as error:
            QMessageBox.warning(self,'Error de portada',str(error))

    def _add_to_active_playlist(self):
        if self.active_playlist is None:
            return
        names = dict(self.db.playlists())
        dlg = AddSongsDialog(self.tracks.values(),names.get(self.active_playlist,'Lista'),self)
        if exec_blurred(dlg,self) == QDialog.DialogCode.Accepted:
            ids = dlg.selected_ids()
            count = self.db.add_many_to_playlist(self.active_playlist,ids)
            self._update_table_context()
            self._refresh_playlist_cards()
            self.statusBar().showMessage(f'{count} canciones agregadas a la lista.',4000)

    def _play_home_song(self,item):
        tid = item.data(Qt.ItemDataRole.UserRole)
        if tid is not None:
            self.playback.replace([tid]+[t for t in self._library_ids() if t != tid])
            self.play_track(tid,queue_index=0)

    def _play_home_playlist(self,item):
        pid = item.data(Qt.ItemDataRole.UserRole)
        if pid is not None:
            self.start_playlist(pid)

    def refresh_library(self, reset_queue=False):
        self.tracks = {t.id:t for t in self.db.all_tracks()}
        if reset_queue:
            self.playback.replace(list(self.tracks))
        else:
            self.playback.prune(set(self.tracks))
        if self.current_id not in self.tracks:
            self.current_id = None
        self.track_model.set_tracks(list(self.tracks.values()))
        self._refresh_filter_options()
        self._update_table_context()
        self.refresh_queue()
        self._update_current_metadata()
        self._refresh_home()
        if self.current_tab == 'Listas' and self.lower_stack.currentIndex() == 2:
            self._refresh_playlist_cards()

    def _refresh_changed_tracks(self, ids):
        for tid in dict.fromkeys(ids):
            updated = self.db.get_track(tid)
            if updated:
                self.tracks[tid] = updated
                self.track_model.replace_track(updated)
        self._update_current_metadata()
        self._update_count()
        if self.current_tab == 'Inicio':
            self._refresh_home()

    def _refresh_filter_options(self):
        genres = sorted({g for t in self.tracks.values() for g in split_genres(t.genre)},key=str.casefold)
        artists = sorted({t.artist for t in self.tracks.values()},key=str.casefold)
        albums = sorted({t.album for t in self.tracks.values()},key=str.casefold)
        values = [
            (self.genre_filter,'Todos los géneros',genres),
            (self.artist_filter,'Todos los artistas',artists),
            (self.album_filter,'Todos los álbumes',albums),
            (self.mood_filter,'Todas las emociones',[(key, val['label']) for key,val in MOODS.items()]),
        ]
        for combo,placeholder,options in values:
            old = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(placeholder,'')
            if combo == self.mood_filter:
                for key,description in options:
                    combo.addItem(description,key)
            else:
                for val in options:
                    combo.addItem(val,val)
            found = combo.findData(old)
            combo.setCurrentIndex(found if found >= 0 else 0)
            combo.blockSignals(False)

    def _update_table_context(self):
        if not hasattr(self,'proxy'):
            return
        wanted = self.db.playlist_track_ids(self.active_playlist) if self.current_tab == 'Listas' and self.active_playlist is not None else []
        self.proxy.set_context(self.current_tab, wanted)
        self.table.setSortingEnabled(self.current_tab != 'Listas')
        if self.current_tab == 'Listas':
            self.proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self._apply_filters()
        self.table.reset_selection_order()

    def _on_search_changed(self, text):
        if text and self.current_tab == 'Inicio':
            self._navigate('Biblioteca')
        self._apply_filters()

    def _apply_filters(self, *unused):
        if not hasattr(self,'proxy'):
            return
        self.proxy.set_filters(self.search.text(),self.genre_filter.currentData() or '',
                               self.artist_filter.currentData() or '',self.album_filter.currentData() or '',
                               self.mood_filter.currentData() or '')
        self._update_count()

    def _update_count(self):
        self.count_text.setText(f'{self.proxy.rowCount()} canciones')

    def _visible_track_ids(self):
        return [self.proxy.index(i,0).data(Qt.ItemDataRole.UserRole) for i in range(self.proxy.rowCount())]

    def _library_ids(self):
        return list(self.tracks)

    def _show_track_menu(self,pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        tid = index.data(Qt.ItemDataRole.UserRole)
        selected = self.table.selected_track_ids()
        if tid not in selected:
            self.table.selectRow(index.row())
            self.table.reset_selection_order()
            selected = [tid]
        selected = [x for x in selected if x in self.tracks]
        if not selected:
            return
        multi = len(selected) > 1
        suffix = f' ({len(selected)})' if multi else ''
        menu = QMenu(self)
        play = menu.addAction('Reproducir selección' + suffix)
        queue = menu.addAction('Añadir a cola' + suffix)
        all_fav = all(self.tracks[x].favorite for x in selected)
        favorite = menu.addAction(('Quitar de favoritos' if all_fav else 'Añadir a favoritos')+suffix)
        moods = menu.addMenu('Asignar emoción')
        auto = moods.addAction('Automático (género)')
        mood_actions = {moods.addAction(value['label']):key for key,value in MOODS.items()}
        edit_genre = menu.addAction('Editar géneros' + suffix)
        edit_file = menu.addAction('Editar metadatos del archivo original…') if not multi else None
        playlists = menu.addMenu('Añadir a lista')
        playlist_actions = {playlists.addAction(name):pid for pid,name in self.db.playlists()}
        new_list = playlists.addAction('＋ Crear lista nueva')
        remove = menu.addAction('Quitar de biblioteca'+suffix)
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == play:
            self.playback.replace(selected)
            self.play_track(selected[0],queue_index=0)
        elif action == queue:
            self.playback.extend(selected)
            self.refresh_queue()
            self.statusBar().showMessage(f'{len(selected)} añadida(s) a la cola.',3000)
        elif action == favorite:
            self.db.set_favorites(selected, not all_fav)
            self._refresh_changed_tracks(selected)
        elif action == auto or action in mood_actions:
            mood = '' if action == auto else mood_actions[action]
            self.db.set_moods(selected,mood)
            self._refresh_changed_tracks(selected)
            if self.current_id in selected:
                self._refresh_mood()
        elif action == edit_genre:
            initial = self.tracks[selected[0]].genre if not multi else ''
            existing = [g for t in self.tracks.values() for g in split_genres(t.genre)]
            dlg = GenreDialog(initial,existing,self)
            if exec_blurred(dlg,self) == QDialog.DialogCode.Accepted:
                self.db.set_genres(selected,dlg.genres())
                self._refresh_changed_tracks(selected)
                self._refresh_filter_options()
                self._apply_filters()
                if self.current_id in selected:
                    self._refresh_mood()
        elif edit_file is not None and action == edit_file:
            self._edit_file_metadata(tid)
        elif action in playlist_actions:
            count = self.db.add_many_to_playlist(playlist_actions[action],selected)
            if self.current_tab == 'Listas' and self.active_playlist == playlist_actions[action]:
                self._update_table_context()
            self.statusBar().showMessage(f'{count} canciones nuevas añadidas a la lista.',3500)
        elif action == new_list:
            new_pid = self.create_playlist()
            if new_pid is not None:
                self.db.add_many_to_playlist(new_pid,selected)
                self._update_table_context()
        elif action == remove:
            if QMessageBox.question(self,'Quitar canciones',
                f'¿Quitar {len(selected)} canción(es) de la biblioteca? Los archivos no se borrarán.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
            if self.current_id in selected:
                self.player.stop()
                self.current_id = None
            self.db.remove_tracks(selected)
            self.refresh_library()
            self._refresh_mood()

    def _edit_file_metadata(self,tid):
        track = self.tracks.get(tid)
        if not track:
            return
        if Path(track.path).suffix.lower() not in WRITABLE_EXTENSIONS:
            QMessageBox.information(self,'Formato no editable',
                'Este archivo no permite guardar metadatos desde Musicavatar.\n'
                'Puedes editar los datos internos de la biblioteca mediante «Editar géneros».')
            return
        dlg = TrackMetadataDialog(track,[g for t in self.tracks.values() for g in split_genres(t.genre)],self)
        if exec_blurred(dlg,self) != QDialog.DialogCode.Accepted:
            return
        if QMessageBox.question(self,'Modificar archivo original',
                'Se modificarán las etiquetas dentro del archivo original. ¿Continuar?\n'
                'Se recomienda tener una copia de seguridad.',
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        if self.current_id == tid and self.player.path:
            self.player.stop()  # En Windows se debe cerrar el archivo para editarlo.
        try:
            write_file_tags(track.path,*dlg.values())
            final_path = Path(track.path)
            if dlg.rename_checkbox.isChecked():
                from .metadata_edit import safe_rename_audio
                new_path = safe_rename_audio(final_path, dlg.title_field.text())
                if new_path != final_path:
                    self.db.update_track_path(tid, str(new_path))
                    final_path = new_path
            updated = read_track(final_path,DATA_DIR/'covers')
            self.db.update_track_metadata(tid,updated)
            _COVER_CACHE.clear()
            self._refresh_changed_tracks([tid])
            self._refresh_filter_options()
            self._apply_filters()
            self._rendered_queue_ids = []
            self.refresh_queue()
            self._refresh_home()
            self.statusBar().showMessage('Título y metadatos actualizados; el archivo conserva su nombre físico salvo que marques renombrar.',5500)
        except Exception as error:
            QMessageBox.warning(self,'No se pudieron guardar los cambios',str(error))

    def _play_table_index(self,index):
        if not index.isValid():
            return
        ids = self._visible_track_ids()
        tid = index.data(Qt.ItemDataRole.UserRole)
        if tid not in ids:
            return
        # Doble clic: comienza en la elegida y continúa con las filas siguientes.
        following = ids[ids.index(tid):]
        self.playback.replace(following)
        if self.current_tab == 'Listas' and self.active_playlist is not None:
            self.db.increment_playlist_play(self.active_playlist)
        self.play_track(tid,queue_index=0)

    def play_all(self, shuffle=False, source='current'):
        ids = self._library_ids() if source == 'home' or self.current_tab == 'Inicio' else self._visible_track_ids()
        if not ids:
            QMessageBox.information(self,'Sin canciones','No hay canciones para reproducir en esta sección o con estos filtros.')
            return
        self.playback.replace(ids)
        self.shuffle_btn.setChecked(shuffle)
        self.toggle_shuffle()
        if self.current_tab == 'Listas' and self.active_playlist is not None and source != 'home':
            self.db.increment_playlist_play(self.active_playlist)
        index = random.randrange(len(ids)) if shuffle else 0
        self.play_track(ids[index],queue_index=index)

    def start_playlist(self,pid,shuffle=False):
        ids = [tid for tid in self.db.playlist_track_ids(pid) if tid in self.tracks]
        if not ids:
            QMessageBox.information(self,'Lista vacía','Esta lista todavía no contiene canciones.')
            self._open_playlist(pid)
            return
        self.db.increment_playlist_play(pid)
        self.playback.replace(ids)
        self.shuffle_btn.setChecked(shuffle)
        self.toggle_shuffle()
        position = random.randrange(len(ids)) if shuffle else 0
        self.play_track(ids[position],queue_index=position)
        self._refresh_home()

    def _play_queue_item(self,item):
        row = self.queue_list.row(item)
        if 0 <= row < len(self.queue):
            self.play_track(self.queue[row],queue_index=row)

    def refresh_queue(self):
        highlighted = self.playback.current_index
        if highlighted is not None and (highlighted >= len(self.queue) or self.queue[highlighted] != self.current_id):
            highlighted = None
        if self._rendered_queue_ids == self.queue and self.queue_list.count() == len(self.queue):
            # Cambiar de canción no exige reconstruir cientos o miles de filas.
            for i in {self._last_highlighted_index, highlighted} - {None}:
                item = self.queue_list.item(i)
                if item:
                    item.setForeground(QColor('#e1c8ff' if i == highlighted else '#e8dfef'))
            if highlighted is not None:
                self.queue_list.setCurrentRow(highlighted)
            else:
                self.queue_list.clearSelection()
            self._last_highlighted_index = highlighted
            return
        self.queue_list.setUpdatesEnabled(False)
        self.queue_list.clear()
        for i, tid in enumerate(self.queue):
            track = self.tracks.get(tid)
            if not track:
                continue
            item = QListWidgetItem(f'{i+1:02d}  {track.title}\n{track.artist}')
            item.setIcon(QIcon(track_pixmap(track,44)))
            item.setData(Qt.ItemDataRole.UserRole,i)
            item.setSizeHint(QSize(210,58))
            if i == highlighted:
                item.setForeground(QColor('#e1c8ff'))
            self.queue_list.addItem(item)
        self._rendered_queue_ids = list(self.queue)
        self._last_highlighted_index = highlighted
        if highlighted is not None and highlighted < self.queue_list.count():
            self.queue_list.setCurrentRow(highlighted)
        self.queue_list.setUpdatesEnabled(True)

    def _queue_menu(self,pos):
        item = self.queue_list.itemAt(pos)
        if not item:
            return
        row = self.queue_list.row(item)
        menu = QMenu(self)
        play = menu.addAction('Reproducir ahora')
        remove = menu.addAction('Quitar de la cola')
        chosen = menu.exec(self.queue_list.viewport().mapToGlobal(pos))
        if chosen == play and row < len(self.queue):
            self.play_track(self.queue[row],queue_index=row)
        elif chosen == remove:
            self.playback.remove(row)
            self.refresh_queue()

    def clear_queue(self):
        self.playback.clear()
        self.refresh_queue()
        self.statusBar().showMessage('Cola vaciada. Usa «Reponer todas» o «Reproducir todo» para llenarla.',4000)

    def restore_full_queue(self):
        self.playback.replace(self._library_ids())
        self.refresh_queue()
        self.statusBar().showMessage(f'Cola reconstruida con {len(self.queue)} canciones.',3000)

    def import_folder(self):
        path = QFileDialog.getExistingDirectory(self,'Selecciona una carpeta de música',str(Path.home()))
        if path:
            self.import_paths([Path(path)])

    def import_files(self):
        exts = ' '.join(f'*{ext}' for ext in sorted(SUPPORTED_EXTENSIONS))
        paths,_ = QFileDialog.getOpenFileNames(self,'Selecciona tus canciones',str(Path.home()),
                                             f'Archivos de audio ({exts});;Todos los archivos (*.*)')
        if paths:
            self.import_paths([Path(p) for p in paths])

    def import_paths(self,paths):
        files = scan_paths(paths)
        if not files:
            QMessageBox.information(self,'Sin canciones','No encontramos archivos de audio compatibles.')
            return
        progress = QProgressDialog('Leyendo etiquetas y portadas…','Cancelar',0,len(files),self)
        progress.setWindowTitle('Importando canciones')
        progress.setMinimumDuration(250)
        added = 0
        errors = []
        for i,path in enumerate(files):
            progress.setValue(i)
            if progress.wasCanceled():
                break
            try:
                info = read_track(path,DATA_DIR/'covers')
                if not info['genre']:
                    info['genre'] = infer_genre_from_words(info['title'],info['album'],path.stem)
                _,created = self.db.add_track(info)
                added += int(created)
            except Exception as error:
                errors.append(f'{path.name}: {error}')
        progress.setValue(len(files))
        self.refresh_library()
        self.statusBar().showMessage(f'{added} importadas · {len(errors)} errores · {len(self.tracks)} en biblioteca',7000)
        if errors:
            QMessageBox.warning(self,'Archivos no importados',
                f'No se pudieron leer {len(errors)} archivo(s):\n\n'+'\n'.join(errors[:6]))

    def play_track(self,tid,queue_index=None,history_cursor=None):
        track = self.tracks.get(tid)
        if not track:
            return False
        if not track.exists:
            QMessageBox.warning(self,'Archivo no encontrado',f'No encontramos «{track.title}».\n{track.path}')
            return False
        if not self.player.load_and_play(track.path):
            return False
        self.current_id = tid
        self.spectrum.set_track(track.path)
        self._position_seconds = 0.0
        self.playback.select(tid,queue_index,history_cursor)
        self.db.increment_track_play(tid)
        self._refresh_changed_tracks([tid])
        self._refresh_mood()
        self.refresh_queue()
        if self.current_tab == 'Inicio':
            self._refresh_home()
        self.statusBar().showMessage('Reproduciendo: '+track.title,3500)
        return True

    def _update_current_metadata(self):
        track = self.tracks.get(self.current_id)
        if not track:
            self.now_title.setText('Nada sonando')
            self.now_artist.setText('Importa tus canciones para comenzar')
            self.cover.setPixmap(track_pixmap(None,54))
            self.favorite_now.setIcon(icon('heart'))
            self.mood_select.blockSignals(True)
            self.mood_select.setCurrentIndex(0)
            self.mood_select.blockSignals(False)
            return
        self.now_title.setText(track.title[:57]+('…' if len(track.title)>57 else ''))
        self.now_artist.setText(track.artist[:57])
        self.cover.setPixmap(track_pixmap(track,54))
        self.favorite_now.setIcon(icon('heart','#ef9ac4' if track.favorite else '#e8dfef'))
        self.mood_select.blockSignals(True)
        idx = self.mood_select.findData(track.mood_override or '')
        self.mood_select.setCurrentIndex(idx if idx >= 0 else 0)
        self.mood_select.blockSignals(False)

    def toggle_play(self):
        if self.current_id is None:
            if self.queue:
                self.play_track(self.queue[0],queue_index=0)
            else:
                QMessageBox.information(self,'Cola vacía','Usa «Reproducir todo» o importa música para empezar.')
            return
        if not self.player.path:
            self.play_track(self.current_id,queue_index=self.playback.current_index)
        else:
            self.player.toggle_pause()
            self._refresh_mood()

    def next_track(self):
        target = self.playback.next_target(self.shuffle,self.repeat)
        if target:
            self.play_track(target[0],queue_index=target[1],history_cursor=target[2])
        elif self.current_id is not None:
            self.player.stop()
            self._refresh_mood()

    def previous_track(self):
        if not self.shuffle and self.current_id is not None and self._position_seconds >= 3 and self.player.path:
            self.player.seek(0)
            return
        target = self.playback.previous_target(self.shuffle,self.repeat)
        if target:
            self.play_track(target[0],queue_index=target[1],history_cursor=target[2])
        elif self.player.path:
            self.player.seek(0)

    def toggle_shuffle(self, *unused):
        self.shuffle = self.shuffle_btn.isChecked()
        self._refresh_mode_buttons()

    def toggle_repeat(self, *unused):
        self.repeat = self.repeat_btn.isChecked()
        self._refresh_mode_buttons()

    def _refresh_mode_buttons(self):
        self.shuffle_btn.setToolTip('Aleatorio ACTIVADO · clic para desactivar' if self.shuffle else 'Aleatorio DESACTIVADO · clic para activar')
        self.repeat_btn.setToolTip('Repetición ACTIVADA · clic para desactivar' if self.repeat else 'Repetición DESACTIVADA · clic para activar')

    def _track_ended(self):
        self.next_track()

    def _state_changed(self, playing):
        self.play_btn.setIcon(icon('pause' if playing else 'play','#1d1627',26))
        self.spectrum.playing = playing
        self.spectrum.update()
        self._refresh_mood()

    def _update_position(self,pos,duration):
        self._position_seconds = pos
        self.spectrum.position = pos
        if not self._seeking:
            self.timeline.blockSignals(True)
            self.timeline.setValue(int(1000*pos/duration) if duration>0 else 0)
            self.timeline.blockSignals(False)
            self.elapsed.setText(format_time(pos))
        track = self.tracks.get(self.current_id)
        self.total.setText(format_time(duration or (track.duration if track else 0)))

    def _seek_start(self):
        self._seeking = True

    def _seek_end(self):
        self._seeking = False
        if self.current_id is None or not self.player.path:
            return
        try:
            duration = (self.player.media.get_length()/1000 if self.player.backend == 'VLC'
                        else self.player._qt_player.duration()/1000)
            if duration > 0:
                self.player.seek(duration*self.timeline.value()/1000)
        except Exception:
            pass

    def _mood_tick(self):
        track = self.tracks.get(self.current_id)
        self.session.update(get_track_mood(track),1.0,bool(track and self.player.is_playing))
        self.mood_time.setText(format_time(self.session.seconds))
        if track and self.player.is_playing:
            mood = get_track_mood(track)
            self._mood_pending[mood] = self._mood_pending.get(mood,0.0)+1.0
            self._mood_flush_ticks += 1
            if self._mood_flush_ticks >= 10:
                self._flush_mood_totals()
                if self.current_tab == 'Inicio':
                    self._refresh_home()
        if self.session.stage != self._last_stage:
            self._refresh_mood()

    def _flush_mood_totals(self):
        for mood,seconds in self._mood_pending.items():
            self.db.add_mood_seconds(mood,seconds)
        self._mood_pending.clear()
        self._mood_flush_ticks = 0

    def change_track_mood(self,*unused):
        # No recargar la tabla ni la base de datos completa durante reproducción.
        if self.current_id is None:
            return
        mood = self.mood_select.currentData() or ''
        self.db.set_mood(self.current_id,mood)
        self._refresh_changed_tracks([self.current_id])
        self._refresh_mood()

    def _refresh_mood(self):
        track = self.tracks.get(self.current_id)
        active = bool(track and self.player.is_playing)
        mood = get_track_mood(track) if track else 'neutral'
        self.session.update(mood,0,active)
        display = mood if active else 'neutral'
        stage = self.session.stage if active else 0
        self.avatar.set_state(display,stage,active)
        self.mood_title.setText(MOODS[mood]['label'] if active else 'Dormido')
        if active:
            description = MOODS[mood]['message']
            if mood == 'sad' and stage == 2:
                description = 'Bajo la lluvia... ¡Necesita otra playlist!'
            elif stage == 1:
                description = 'Lleva un buen rato en este ambiente.'
            self.mood_description.setText(description)
            self.avatar_caption.setText('♫  Este mundo sigue el ritmo')
        else:
            self.mood_description.setText('Pausa musical: el avatar descansa.')
            self.avatar_caption.setText('☾  Descansando en su pequeño mundo')
        mood_icons = {'neutral':'☾','happy':'☀','sad':'☂','calm':'☁','energy':'ϟ','love':'♥'}
        self.mood_icon.setText(mood_icons[display])
        self.mood_icon.setStyleSheet('font-size:28px;font-weight:900;color:'+MOODS[display]['accent']+';')
        if self._last_mood != display:
            self.main_panel.set_mood(display)
            self.right_panel.set_mood(display)
            self._last_mood = display
        self._last_stage = stage
        self.mood_time.setText(format_time(self.session.seconds))
        self.mood_explain.setText('Sin género: asigna una emoción manualmente.' if track and not track.genre and not track.mood_override
                                  else 'Emoción automática por género o selección manual.')

    def favorite_current(self):
        if self.current_id is None:
            return
        self.db.toggle_favorite(self.current_id)
        self._refresh_changed_tracks([self.current_id])

    def _populate_playlist_picker(self):
        current = self.active_playlist
        self.playlist_picker.blockSignals(True)
        self.playlist_picker.clear()
        for pid,name in self.db.playlists():
            self.playlist_picker.addItem(name,pid)
        idx = self.playlist_picker.findData(current) if current is not None else -1
        if idx >= 0:
            self.playlist_picker.setCurrentIndex(idx)
        self.active_playlist = self.playlist_picker.currentData()
        self.playlist_picker.blockSignals(False)

    def create_playlist(self):
        name, ok = QInputDialog.getText(self,'Nueva lista','Nombre de la lista de reproducción:')
        if not ok:
            return None
        if not self.db.create_playlist(name):
            QMessageBox.warning(self,'Nombre inválido','El nombre no puede estar vacío ni repetido.')
            return None
        pid = next(pid for pid,title in self.db.playlists() if title == name.strip())
        if self.current_tab != 'Listas':
            self._navigate('Listas')
        dlg = AddSongsDialog(self.tracks.values(),name.strip(),self)
        if exec_blurred(dlg,self) == QDialog.DialogCode.Accepted:
            self.db.add_many_to_playlist(pid,dlg.selected_ids())
        self._refresh_playlist_cards()
        self._open_playlist(pid)
        self.statusBar().showMessage('Lista creada. Puedes añadir más canciones cuando quieras.',3500)
        return pid

    def _on_playlist_selection(self,*unused):
        self.active_playlist = self.playlist_picker.currentData()
        if self.current_tab == 'Listas' and self.active_playlist is not None:
            self.list_title.setText(self.playlist_picker.currentText())
            self._update_table_context()

    def keyPressEvent(self,event):
        if event.key() == Qt.Key.Key_Space and not isinstance(self.focusWidget(),(QLineEdit,QComboBox)):
            self.toggle_play()
            event.accept()
            return
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_O:
            self.import_files()
            event.accept()
            return
        super().keyPressEvent(event)

    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self,event):
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.import_paths(paths)
            event.acceptProposedAction()

    def closeEvent(self,event):
        self.db.set_setting('volume',str(self.volume.value()))
        self.db.set_setting('split_h_v03',base64.b64encode(bytes(self.horizontal_splitter.saveState())).decode())
        self.db.set_setting('split_v',base64.b64encode(bytes(self.vertical_splitter.saveState())).decode())
        self._flush_mood_totals()
        self.spectrum._analyzer.stop()
        self.player.stop()
        self.db.close()
        event.accept()
