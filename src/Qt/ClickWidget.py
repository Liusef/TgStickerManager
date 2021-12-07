from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal


class ClickWidget(QWidget):

    clicked = Signal()

    def click(self):
        self.clicked.emit()

    def mousePressEvent(self, event:QMouseEvent) -> None:
        self.clicked.emit()

    def setCentralWidget(self, widget: QWidget) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        self.setLayout(layout)