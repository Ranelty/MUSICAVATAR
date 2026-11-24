"""Espectro real del archivo local, precalculado en segundo plano y dibujado por Qt.

No captura el audio del sistema, no modifica el motor VLC y solo decodifica
cuando el usuario activa el visualizador. Frames compactos ~11 Hz con FFT.
"""
from __future__ import annotations
import subprocess
import threading
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


class _Analyzer(QObject):
    ready = Signal(int, object)
    failed = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial = 0
        self.cancel = threading.Event()
        self.process = None

    def request(self, filename: str):
        self.cancel.set()
        if self.process is not None:
            try:
                self.process.terminate()
            except OSError:
                pass
        self.serial += 1
        serial = self.serial
        self.cancel = threading.Event()
        cancel = self.cancel
        threading.Thread(target=self._work, args=(serial, filename, cancel), daemon=True).start()

    def stop(self):
        self.cancel.set()
        if self.process is not None:
            try:
                self.process.terminate()
            except OSError:
                pass
        self.serial += 1

    def _work(self, serial, filename, cancel):
        proc = None
        try:
            import numpy as np
            import imageio_ffmpeg
            if not Path(filename).is_file():
                return
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            args = [ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error',
                    '-i', filename, '-vn', '-ac', '1', '-ar', '11025',
                    '-f', 's16le', '-acodec', 'pcm_s16le', '-']
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.process = proc
            sample_rate = 11025
            nfft = 2048
            hop = 1024
            freq = np.fft.rfftfreq(nfft, 1/sample_rate)
            edges = np.geomspace(45, 5200, 65)
            ranges = [(max(1, int(np.searchsorted(freq, edges[i]))),
                       min(len(freq), max(2, int(np.searchsorted(freq, edges[i+1]))))) for i in range(64)]
            window = np.hanning(nfft)
            pending = np.zeros(0, dtype=np.float32)
            frames = []
            # Intervalos de ~93 ms. Solo guardamos el espectro, no el PCM.
            while not cancel.is_set():
                chunk = proc.stdout.read(8192)
                if not chunk:
                    break
                pcm = np.frombuffer(chunk, dtype='<i2').astype(np.float32) / 32768.0
                pending = np.concatenate((pending, pcm))
                while len(pending) >= nfft:
                    magnitudes = np.abs(np.fft.rfft(pending[:nfft] * window))
                    power = np.array([np.max(magnitudes[a:max(a+1,b)]) for a,b in ranges], dtype=np.float32)
                    # Compresión suave (dinámica musical, no volumen fijo).
                    levels = np.clip(np.log1p(power * 2.0) / 6.0, 0.0, 1.0)
                    frames.append(np.asarray(np.rint(levels*255), dtype=np.uint8).tobytes())
                    if len(frames) % 48 == 0 and not cancel.is_set():
                        self.ready.emit(serial, frames.copy())
                    pending = pending[hop:]
            proc.wait(timeout=3)
            if not cancel.is_set():
                self.ready.emit(serial, frames)
        except Exception as exc:
            if not cancel.is_set():
                self.failed.emit(serial, str(exc))
        finally:
            if proc is not None and proc.poll() is None:
                proc.terminate()
            if self.process is proc:
                self.process = None


class SpectrumWidget(QWidget):
    """32/64 barras con color configurable. Se pausa totalmente cuando está oculto."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(72)
        self.setMaximumHeight(105)
        self.bars = 32
        self.color = '#bc93ea'
        self.frames = []
        self.position = 0.0
        self.playing = False
        self._analyzer = _Analyzer(self)
        self._analyzer.ready.connect(self._receive)
        self._analyzer.failed.connect(self._fail)
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._tick)
        self.hide()

    def set_enabled(self, enabled):
        self.setVisible(enabled)
        if enabled:
            self.timer.start()
        else:
            self.timer.stop()
            self._analyzer.stop()
            self.frames = []

    def set_track(self, path):
        self.frames = []
        self.position = 0.0
        if self.isVisible() and path:
            self._analyzer.request(path)
        else:
            self._analyzer.stop()
        self.update()

    def _receive(self, serial, frames):
        if serial == self._analyzer.serial:
            self.frames = frames
            self.update()

    def _fail(self, serial, message):
        if serial == self._analyzer.serial:
            self.frames = []

    def _tick(self):
        if self.playing:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), QColor(16, 13, 22, 125))
        w = self.width()
        h = self.height()
        margin = 14
        count = self.bars
        step = max(1.0, (w - margin*2)/count)
        width = max(2, int(step*0.58))
        pos = int(self.position * 11025/1024)
        bands = self.frames[min(pos, len(self.frames)-1)] if self.frames else [0.02]*64
        for i in range(count):
            chunk = bands[i*64//count:(i+1)*64//count]
            level = (max(chunk)/255.0) if chunk else 0
            height = max(3, int(level * (h-16)))
            painter.fillRect(int(margin+i*step), (h-height)//2, width, height, QColor(self.color))
        painter.end()

    def close(self):
        self._analyzer.stop()
        super().close()
