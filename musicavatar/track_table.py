"""Tabla de canciones eficiente: modelo Qt + filtros, sin reconstruir miles de celdas."""
from __future__ import annotations
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QTableView
from .genres import split_genres
from .moods import get_track_mood


class TrackModel(QAbstractTableModel):
    COLUMNS = ('CANCIÓN', 'ARTISTA', 'ÁLBUM', 'GÉNEROS', 'DURACIÓN')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracks = []
        self.row_by_id = {}

    def set_tracks(self, tracks):
        self.beginResetModel()
        self.tracks = list(tracks)
        self.row_by_id = {track.id: i for i, track in enumerate(self.tracks)}
        self.endResetModel()

    def replace_track(self, track):
        i = self.row_by_id.get(track.id)
        if i is not None:
            self.tracks[i] = track
            self.dataChanged.emit(self.index(i, 0), self.index(i, 4))

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.tracks)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self.tracks):
            return None
        track = self.tracks[index.row()]
        if role == Qt.ItemDataRole.UserRole:
            return track.id
        if role == Qt.ItemDataRole.ToolTipRole:
            return track.path if index.column() == 0 else None
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() == 4:
            return int(Qt.AlignmentFlag.AlignCenter)
        if role == Qt.ItemDataRole.DisplayRole:
            from .utils import format_time
            return [f'♥  {track.title}' if track.favorite else track.title,
                    track.artist, track.album, track.genre or 'Sin género',
                    format_time(track.duration)][index.column()]
        return None


class TrackFilter(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab = 'Biblioteca'
        self.playlist_ids = set()
        self.playlist_order = {}
        self.search_text = ''
        self.genre = ''
        self.artist = ''
        self.album = ''
        self.mood = ''
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setDynamicSortFilter(True)

    def set_context(self, tab, playlist_ids=None):
        self.tab = tab
        self.playlist_ids = set(playlist_ids or [])
        self.playlist_order = {tid: i for i, tid in enumerate(playlist_ids or [])}
        self.invalidateFilter()

    def set_filters(self, query='', genre='', artist='', album='', mood=''):
        self.search_text = query.casefold().strip()
        self.genre = genre.casefold()
        self.artist = artist.casefold()
        self.album = album.casefold()
        self.mood = mood
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        track = self.sourceModel().tracks[source_row]
        if self.tab == 'Favoritos' and not track.favorite:
            return False
        if self.tab == 'Listas' and track.id not in self.playlist_ids:
            return False
        if self.search_text and self.search_text not in f'{track.title} {track.artist} {track.album} {track.genre}'.casefold():
            return False
        if self.genre and not any(part.casefold() == self.genre for part in split_genres(track.genre)):
            return False
        if self.artist and track.artist.casefold() != self.artist:
            return False
        if self.album and track.album.casefold() != self.album:
            return False
        if self.mood and get_track_mood(track) != self.mood:
            return False
        return True

    def lessThan(self, left, right):
        # Las listas de reproducción usan posición original; el orden se controla desde la vista.
        a = self.sourceModel().tracks[left.row()]
        b = self.sourceModel().tracks[right.row()]
        if self.tab == 'Listas':
            return self.playlist_order.get(a.id, 10**12) < self.playlist_order.get(b.id, 10**12)
        col = left.column()
        if col == 4:
            return a.duration < b.duration
        return [a.title, a.artist, a.album, a.genre][col].casefold() < [b.title, b.artist, b.album, b.genre][col].casefold()


class OrderedTrackView(QTableView):
    """Ctrl conserva secuencia de clics; Shift devuelve filas en orden visual."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._click_order = []
        self._selection_mode = 'table'

    def mousePressEvent(self, event):
        index = self.indexAt(event.position().toPoint())
        if event.button() == Qt.MouseButton.RightButton and index.isValid():
            already = any(idx.row() == index.row() for idx in self.selectionModel().selectedRows())
            if already:
                event.accept()
                return
        super().mousePressEvent(event)
        if event.button() != Qt.MouseButton.LeftButton or not index.isValid():
            return
        current = self._selected_in_row_order()
        tid = index.data(Qt.ItemDataRole.UserRole)
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            self._selection_mode = 'range'
            self._click_order = current
        elif modifiers & Qt.KeyboardModifier.ControlModifier:
            self._selection_mode = 'ctrl'
            self._click_order = [x for x in self._click_order if x in current and x != tid]
            if tid in current:
                self._click_order.append(tid)
            for x in current:
                if x not in self._click_order:
                    self._click_order.append(x)
        else:
            self._selection_mode = 'table'
            self._click_order = current

    def _selected_in_row_order(self):
        rows = sorted(self.selectionModel().selectedRows(), key=lambda ix: ix.row())
        return [row.data(Qt.ItemDataRole.UserRole) for row in rows]

    def selected_track_ids(self):
        current = self._selected_in_row_order()
        if self._selection_mode == 'ctrl':
            return [x for x in self._click_order if x in current] + [x for x in current if x not in self._click_order]
        return current

    def reset_selection_order(self):
        self._selection_mode = 'table'
        self._click_order = []
