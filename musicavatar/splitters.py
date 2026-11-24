"""Separadores arrastrables con ancho visual estrictamente acotado."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QSplitterHandle


class CompactSplitter(QSplitter):
    def createHandle(self):
        handle = QSplitterHandle(self.orientation(), self)
        if self.orientation() == Qt.Orientation.Horizontal:
            handle.setFixedWidth(5)
        else:
            handle.setFixedHeight(5)
        return handle
