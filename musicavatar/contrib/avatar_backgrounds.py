"""Contribución 2: fondo local, ajuste y oscurecimiento para el escenario pixel art.

Solo necesita el puente de integración ya publicado por el integrador. La imagen
se guarda en data/ (excluida de Git), sin modificar los archivos de música.
"""
from __future__ import annotations
import os
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QImageReader
from PySide6.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QMessageBox, QSlider, QScrollArea,
)
from .background_rules import (
    validate_image_path, normalize_fit, clamp_dim, stored_background_path,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class BackgroundControls(QGroupBox):
    def __init__(self, window):
        super().__init__('Fondo del escenario')
        self.window = window
        self.background_file = stored_background_path(PROJECT_ROOT)
        self._cached_pixmap: QPixmap | None = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 13, 10, 12)
        lay.setSpacing(7)
        help_text = QLabel('Usa una imagen propia detrás del personaje. No cambia el fondo de la aplicación.')
        help_text.setWordWrap(True)
        help_text.setObjectName('Muted')
        lay.addWidget(help_text)
        self.preview = QLabel('Escenario original')
        self.preview.setMinimumHeight(75)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet('border:1px solid #51415b;border-radius:7px;')
        lay.addWidget(self.preview)
        row = QHBoxLayout()
        choose = QPushButton('Elegir imagen…')
        choose.clicked.connect(self.choose_image)
        row.addWidget(choose)
        reset = QPushButton('Restaurar')
        reset.clicked.connect(self.reset_background)
        row.addWidget(reset)
        lay.addLayout(row)
        lay.addWidget(QLabel('Ajuste de imagen'))
        self.fit = QComboBox()
        self.fit.addItem('Rellenar (recorte centrado)', 'cover')
        self.fit.addItem('Ajustar (imagen completa)', 'contain')
        self.fit.currentIndexChanged.connect(self.save_options)
        lay.addWidget(self.fit)
        self.dim_text = QLabel('Oscurecimiento: 0 %')
        lay.addWidget(self.dim_text)
        self.dim = QSlider(Qt.Orientation.Horizontal)
        self.dim.setRange(0, 80)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(250)
        self._save_timer.timeout.connect(self.save_options)
        self.dim.valueChanged.connect(self._preview_change)
        self.dim.sliderReleased.connect(self.save_options)
        lay.addWidget(self.dim)
        self._load_saved()

    def _load_saved(self):
        fit = normalize_fit(self.window.db.get_setting('avatar_background_fit', 'cover'))
        i = self.fit.findData(fit)
        self.fit.blockSignals(True)
        self.fit.setCurrentIndex(max(0, i))
        self.fit.blockSignals(False)
        value = clamp_dim(self.window.db.get_setting('avatar_background_dim', '0'))
        self.dim.blockSignals(True)
        self.dim.setValue(value)
        self.dim.blockSignals(False)
        self.dim_text.setText(f'Oscurecimiento: {value} %')
        self._apply_image()

    def _load_pixmap(self) -> QPixmap | None:
        if self._cached_pixmap is not None:
            return self._cached_pixmap
        if not self.background_file.is_file():
            return None
        pix = QPixmap(str(self.background_file))
        self._cached_pixmap = None if pix.isNull() else pix
        return self._cached_pixmap

    def _apply_image(self):
        pix = self._load_pixmap()
        if pix:
            thumb = pix.scaled(QSize(235, 90), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
            self.preview.setPixmap(thumb)
        else:
            self.preview.clear()
            self.preview.setText('Escenario original')
        self.window.avatar.set_background_image(pix, self.fit.currentData() or 'cover', self.dim.value())

    def _preview_change(self, value):
        self.dim_text.setText(f'Oscurecimiento: {value} %')
        self.window.avatar.set_background_image(self._load_pixmap(), self.fit.currentData() or 'cover', value)
        self._save_timer.start()

    def save_options(self, *args):
        self._save_timer.stop()
        fit = normalize_fit(self.fit.currentData() or 'cover')
        dim = clamp_dim(self.dim.value())
        self.window.db.set_setting('avatar_background_fit', fit)
        self.window.db.set_setting('avatar_background_dim', str(dim))
        self._apply_image()

    def choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Imagen para tu escenario', str(Path.home()),
                                'Imágenes (*.png *.jpg *.jpeg *.webp)')
        if not path:
            return
        try:
            validated = validate_image_path(path)
            reader = QImageReader(str(validated))
            reader.setAutoTransform(True)
            if not reader.canRead():
                raise ValueError('No se pudo leer el contenido de la imagen.')
            original = reader.size()
            if original.isValid() and (original.width() > 10000 or original.height() > 10000):
                raise ValueError('Dimensiones demasiado grandes para el escenario.')
            if original.isValid() and max(original.width(), original.height()) > 768:
                fraction = 768 / max(original.width(), original.height())
                reader.setScaledSize(QSize(max(1,round(original.width()*fraction)),
                                           max(1,round(original.height()*fraction))))
            image = reader.read()
            if image.isNull():
                raise ValueError(reader.errorString() or 'Imagen no compatible.')
            self.background_file.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.background_file.with_suffix('.tmp.png')
            if not image.save(str(temporary), 'PNG'):
                raise OSError('No fue posible guardar la imagen del escenario.')
            os.replace(temporary, self.background_file)
            self._cached_pixmap = None
            self._apply_image()
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, 'No se pudo cargar el fondo', str(exc))

    def reset_background(self):
        try:
            self.background_file.unlink(missing_ok=True)
            self._cached_pixmap = None
        except OSError as exc:
            QMessageBox.warning(self, 'No se pudo restaurar', str(exc))
            return
        self._apply_image()


def install(window):
    """Añade controles a Personalizar, sin editar ui.py ni la base de datos."""
    if not hasattr(window.avatar, 'set_background_image'):
        raise RuntimeError('Instala antes el puente de integración del equipo.')
    panel = window.right_stack.widget(1)
    scroll = panel.findChild(QScrollArea)
    if scroll is None or scroll.widget() is None:
        raise RuntimeError('No se encontró la sección desplazable de Personalizar.')
    fields = scroll.widget().layout()
    controls = BackgroundControls(window)
    # Colocar al final de las opciones de ropa; accesible al desplazarse.
    fields.insertWidget(max(0, fields.count()-2), controls)
    window.team_background_controls = controls  # retiene referencia para toda la sesión
    return controls
