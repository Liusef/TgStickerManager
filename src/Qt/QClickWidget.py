from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class QClickWidget(QWidget):

    clicked = Signal()

    def click(self):
        self.clicked.emit()

    def mousePressEvent(self, event:QMouseEvent) -> None:
        self.clicked.emit()