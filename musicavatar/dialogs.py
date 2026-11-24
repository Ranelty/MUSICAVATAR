"""Ventanas de edición y selección de Musicavatar.

Los diálogos nunca escriben archivos por sí solos; el controlador confirma y guarda.
"""
from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QFileDialog, QDialogButtonBox,
    QMessageBox, QGraphicsBlurEffect, QMainWindow, QCheckBox,
)
from .genres import GENRE_CATALOG, genre_suggestions, normalize_genres, split_genres


def exec_blurred(dialog: QDialog, parent) -> int:
    """Difumina solo la ventana de fondo mientras el editor modal está abierto."""
    root = parent.centralWidget() if isinstance(parent, QMainWindow) else None
    if root is None or root.graphicsEffect():
        return dialog.exec()
    blur = QGraphicsBlurEffect(root)
    blur.setBlurRadius(6)
    root.setGraphicsEffect(blur)
    try:
        return dialog.exec()
    finally:
        root.setGraphicsEffect(None)


class GenreDialog(QDialog):
    def __init__(self, initial='', existing=(), parent=None):
        super().__init__(parent)
        self.setWindowTitle('Organizar géneros')
        self.setMinimumWidth(420)
        self._chosen = split_genres(initial)
        layout = QVBoxLayout(self)
        layout.setSpacing(9)
        layout.addWidget(QLabel('Géneros seleccionados (puedes añadir varios):'))
        self.selected = QListWidget()
        self.selected.setMaximumHeight(115)
        layout.addWidget(self.selected)
        self._show_chosen()
        row = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText('Busca o escribe un género, por ejemplo «roc»')
        self.entry.textChanged.connect(self._suggest)
        self.entry.returnPressed.connect(self._add)
        row.addWidget(self.entry)
        add = QPushButton('Añadir')
        add.clicked.connect(self._add)
        row.addWidget(add)
        layout.addLayout(row)
        layout.addWidget(QLabel('Sugerencias del catálogo (doble clic para añadir):'))
        self.suggestions = QListWidget()
        self.suggestions.setMaximumHeight(150)
        self.suggestions.itemDoubleClicked.connect(lambda item: self._add(item.text()))
        layout.addWidget(self.suggestions)
        self._existing = list(existing)
        self._suggest('')
        delete = QPushButton('Quitar género seleccionado')
        delete.clicked.connect(self._remove)
        layout.addWidget(delete)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _show_chosen(self):
        self.selected.clear()
        self.selected.addItems(self._chosen)

    def _suggest(self, query):
        self.suggestions.clear()
        self.suggestions.addItems(genre_suggestions(query, [*GENRE_CATALOG, *getattr(self,'_existing',[])]))

    def _add(self, name=None):
        value = (name if isinstance(name, str) else self.entry.text()).strip()
        if not value:
            return
        matches = genre_suggestions(value, self._existing)
        exact = next((x for x in matches if x.casefold() == value.casefold()), None)
        if exact:
            value = exact
        elif matches and value.casefold() not in [x.casefold() for x in matches]:
            guess = matches[0]
            if QMessageBox.question(self, 'Sugerencia de género',
                    f'¿Te referías a «{guess}» en lugar de «{value}»?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                value = guess
        self._chosen = split_genres([*self._chosen, value])
        self.entry.clear()
        self._show_chosen()

    def _remove(self):
        item = self.selected.currentItem()
        if item:
            self._chosen = [x for x in self._chosen if x != item.text()]
            self._show_chosen()

    def genres(self) -> str:
        return normalize_genres(self._chosen)


class TrackMetadataDialog(QDialog):
    def __init__(self, track, existing_genres=(), parent=None):
        super().__init__(parent)
        self.setWindowTitle('Editar metadatos del archivo original')
        self.setMinimumWidth(470)
        self.image_bytes = None
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        notice = QLabel('Estos cambios se guardarán en el archivo de música original.\n'
                        'Se recomienda tener una copia de seguridad de tus canciones.')
        notice.setWordWrap(True)
        layout.addWidget(notice)
        self.title_field = QLineEdit(track.title)
        self.artist_field = QLineEdit(track.artist)
        self.album_field = QLineEdit(track.album)
        self.genre_field = QLineEdit(track.genre)
        self.genre_field.setPlaceholderText('Ej. Rock, OST, J-Pop (separados por comas)')
        for caption, widget in [('Título',self.title_field),('Artista',self.artist_field),
                                 ('Álbum',self.album_field),('Géneros',self.genre_field)]:
            layout.addWidget(QLabel(caption))
            layout.addWidget(widget)
        self.rename_checkbox = QCheckBox('Renombrar también el archivo de audio en la carpeta (opcional)')
        self.rename_checkbox.setToolTip('Cambiar el título de la canción no implica renombrar el archivo de Windows.')
        layout.addWidget(self.rename_checkbox)
        browse = QPushButton('Seleccionar géneros del catálogo…')
        browse.clicked.connect(lambda: self._choose_genres(existing_genres))
        layout.addWidget(browse)
        row = QHBoxLayout()
        self.cover = QLabel('Sin portada')
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setFixedSize(105,105)
        self.cover.setStyleSheet('background:#292331;border:1px solid #4d4059;border-radius:8px')
        if track.cover and Path(track.cover).is_file():
            self._update_cover(QPixmap(track.cover))
        row.addWidget(self.cover)
        choose = QPushButton('Cambiar carátula JPG/PNG…')
        choose.clicked.connect(self._choose_cover)
        row.addWidget(choose)
        layout.addLayout(row)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText('Guardar en el archivo')
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _choose_genres(self, existing):
        dlg = GenreDialog(self.genre_field.text(), existing, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.genre_field.setText(dlg.genres())

    def _update_cover(self, pix):
        if not pix.isNull():
            self.cover.setPixmap(pix.scaled(104,104,Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation))

    def _choose_cover(self):
        path,_ = QFileDialog.getOpenFileName(self,'Elige portada',str(Path.home()),'Imágenes (*.jpg *.jpeg *.png)')
        if not path:
            return
        try:
            data = Path(path).read_bytes()
            from .metadata_edit import cover_mime
            cover_mime(data)
            if len(data) > 6 * 1024 * 1024:
                raise ValueError('La imagen debe pesar menos de 6 MB.')
            pix = QPixmap()
            if not pix.loadFromData(data):
                raise ValueError('No se puede abrir esta imagen.')
            self.image_bytes = data
            self._update_cover(pix)
        except (ValueError, OSError) as error:
            QMessageBox.warning(self,'Portada inválida',str(error))

    def _validate(self):
        if not self.title_field.text().strip():
            QMessageBox.warning(self,'Falta el título','Escribe el título de la canción.')
            return
        self.accept()

    def values(self):
        return (self.title_field.text().strip(),self.artist_field.text().strip(),
                self.album_field.text().strip(),normalize_genres(self.genre_field.text()),
                self.image_bytes)


class AddSongsDialog(QDialog):
    """Añade múltiples canciones a una lista; filtros y selección persistente."""
    def __init__(self, tracks, playlist_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Añadir canciones a '+playlist_name)
        self.setMinimumSize(630,490)
        self.tracks = list(tracks)
        self.marked: set[int] = set()
        self._loading = False
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Marca las canciones que quieras. Puedes dejarlas para después.'))
        filters = QHBoxLayout()
        self.genre = QComboBox()
        self.artist = QComboBox()
        self.sort = QComboBox()
        from .genres import split_genres
        self.genre.addItem('Todos los géneros','')
        for g in sorted({g for t in tracks for g in split_genres(t.genre)},key=str.casefold):
            self.genre.addItem(g,g)
        self.artist.addItem('Todos los artistas','')
        for a in sorted({t.artist for t in tracks},key=str.casefold):
            self.artist.addItem(a,a)
        self.sort.addItem('Título (A-Z)','title')
        self.sort.addItem('Artista (A-Z)','artist')
        self.sort.addItem('Género (A-Z)','genre')
        self.search = QLineEdit()
        self.search.setPlaceholderText('Buscar canción…')
        for widget in (self.genre,self.artist,self.sort,self.search):
            filters.addWidget(widget)
            if isinstance(widget,QComboBox):
                widget.currentIndexChanged.connect(self._refill)
            else:
                widget.textChanged.connect(self._refill)
        layout.addLayout(filters)
        self.list = QListWidget()
        self.list.itemChanged.connect(self._changed)
        layout.addWidget(self.list,1)
        self.counter = QLabel('0 seleccionadas')
        layout.addWidget(self.counter)
        buttons = QHBoxLayout()
        later = QPushButton('Después agrego')
        later.clicked.connect(self.reject)
        buttons.addWidget(later)
        buttons.addStretch()
        save = QPushButton('Añadir seleccionadas')
        save.setObjectName('Primary')
        save.clicked.connect(self.accept)
        buttons.addWidget(save)
        layout.addLayout(buttons)
        self._refill()

    def _refill(self,*unused):
        self._loading = True
        self.list.clear()
        genre = self.genre.currentData() or ''
        artist = self.artist.currentData() or ''
        query = self.search.text().casefold().strip()
        key = self.sort.currentData() or 'title'
        for track in sorted(self.tracks,key=lambda t:getattr(t,key,'').casefold()):
            if genre and genre not in split_genres(track.genre):
                continue
            if artist and artist != track.artist:
                continue
            if query and query not in (track.title+' '+track.artist+' '+track.album).casefold():
                continue
            item = QListWidgetItem(f'{track.title}  ·  {track.artist}')
            item.setData(Qt.ItemDataRole.UserRole,track.id)
            item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if track.id in self.marked else Qt.CheckState.Unchecked)
            self.list.addItem(item)
        self._loading = False

    def _changed(self,item):
        if self._loading:
            return
        tid = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            self.marked.add(tid)
        else:
            self.marked.discard(tid)
        self.counter.setText(f'{len(self.marked)} seleccionadas')

    def selected_ids(self):
        # El orden se conserva tal como se muestra en la selección por defecto.
        return [t.id for t in sorted(self.tracks,key=lambda t:t.title.casefold()) if t.id in self.marked]
