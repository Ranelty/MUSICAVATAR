"""Reproducción local: primero LibVLC, con alternativa Qt Multimedia."""
from __future__ import annotations
import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, QUrl, Signal


class AudioPlayer(QObject):
    position_changed = Signal(float, float)
    ended = Signal()
    error = Signal(str)
    state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.backend = None
        self.engine = None
        self.audio = None
        self.media = None
        self.path = ''
        self.is_playing = False
        self._duration = 0.0
        self._seeking = False
        self._init_engine()
        self.timer = QTimer(self)
        self.timer.setInterval(350)
        self.timer.timeout.connect(self._poll)
        self.timer.start()

    def _init_engine(self):
        # Windows: intenta encontrar la instalación habitual de VLC de 64 bits.
        if sys.platform == 'win32':
            roots = (Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / 'VideoLAN/VLC',
                     Path('C:/Program Files/VideoLAN/VLC'))
            for root in roots:
                if (root / 'libvlc.dll').exists():
                    os.environ['PATH'] = str(root) + os.pathsep + os.environ.get('PATH', '')
                    if hasattr(os, 'add_dll_directory'):
                        self._vlc_dll_dir = os.add_dll_directory(str(root))
                    break
        try:
            import vlc
            self._vlc = vlc
            self.engine = vlc.Instance('--no-video', '--quiet', '--no-media-library')
            if self.engine is None:
                raise RuntimeError('No se pudo inicializar LibVLC')
            self.media = self.engine.media_player_new()
            self.backend = 'VLC'
            return
        except Exception:
            pass
        try:
            from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
            self._qt_player = QMediaPlayer(self)
            self.audio = QAudioOutput(self)
            self._qt_player.setAudioOutput(self.audio)
            self._qt_player.mediaStatusChanged.connect(self._qt_media_status)
            self._qt_player.errorOccurred.connect(lambda *args: self.error.emit(self._qt_player.errorString()))
            self.backend = 'Qt Multimedia'
        except Exception as e:
            self.backend = None
            self._startup_error = str(e)

    def load_and_play(self, path: str) -> bool:
        if not Path(path).is_file():
            self.error.emit('No encontramos el archivo. Quizá cambió de carpeta o fue eliminado.')
            return False
        if not self.backend:
            self.error.emit('Falta el motor de audio. Instala VLC de 64 bits e inténtalo de nuevo.')
            return False
        try:
            self.path = path
            self.is_playing = False
            if self.backend == 'VLC':
                media = self.engine.media_new_path(str(Path(path).resolve()))
                self.media.set_media(media)
                code = self.media.play()
                if code == -1:
                    self.error.emit('No fue posible reproducir este archivo con VLC.')
                    return False
            else:
                self._qt_player.setSource(QUrl.fromLocalFile(str(Path(path).resolve())))
                self._qt_player.play()
            self.is_playing = True
            self.state_changed.emit(True)
            return True
        except Exception as e:
            self.error.emit('Error al reproducir: ' + str(e))
            return False

    def toggle_pause(self):
        if not self.path:
            return
        if self.backend == 'VLC':
            if self.is_playing:
                self.media.set_pause(1)
            else:
                self.media.set_pause(0)
        elif self.backend == 'Qt Multimedia':
            self._qt_player.pause() if self.is_playing else self._qt_player.play()
        self.is_playing = not self.is_playing
        self.state_changed.emit(self.is_playing)

    def stop(self):
        if self.backend == 'VLC':
            self.media.stop()
        elif self.backend == 'Qt Multimedia':
            self._qt_player.stop()
        self.path = ''
        self.is_playing = False
        self.state_changed.emit(False)
        self.position_changed.emit(0, 0)

    def set_volume(self, volume: int):
        if self.backend == 'VLC':
            self.media.audio_set_volume(volume)
        elif self.backend == 'Qt Multimedia':
            self.audio.setVolume(max(0, min(100, volume)) / 100.0)

    def seek(self, seconds: float):
        if self.backend == 'VLC':
            self.media.set_time(max(0, int(seconds * 1000)))
        elif self.backend == 'Qt Multimedia':
            self._qt_player.setPosition(max(0, int(seconds * 1000)))

    def _qt_media_status(self, status):
        from PySide6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self.path:
            self.is_playing = False
            self.state_changed.emit(False)
            self.ended.emit()

    def _poll(self):
        if not self.path or not self.backend:
            return
        if self.backend == 'VLC':
            state = self.media.get_state()
            if state == self._vlc.State.Ended:
                self.is_playing = False
                self.state_changed.emit(False)
                self.path = ''  # evita emitir ended repetidamente
                self.ended.emit()
                return
            if state == self._vlc.State.Error:
                self.path = ''
                self.is_playing = False
                self.state_changed.emit(False)
                self.error.emit('VLC no pudo decodificar este archivo.')
                return
            position_ms = self.media.get_time()
            duration_ms = self.media.get_length()
        else:
            position_ms = self._qt_player.position()
            duration_ms = self._qt_player.duration()
        self.position_changed.emit(max(0, position_ms) / 1000, max(0, duration_ms) / 1000)
