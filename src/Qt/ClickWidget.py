from PySide6.QtGui import QMouseEvent, QEnterEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QEvent


class ClickWidget(QWidget):
    """
    A Clickable QWidget
    """

    clicked = Signal()

    def click(self):
        self.clicked.emit()

    def mousePressEvent(self, event:QMouseEvent) -> None:
        self.clicked.emit()

    def setCentralWidget(self, widget: QWidget) -> None:
        """
        Sets the widget in the ClickWidget (so there's only one)
        :param widget: The widget to set in the Widget
        :return: None
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        self.setLayout(layout)


class LitClickWidget(ClickWidget):
    def enterEvent(self, event:QEnterEvent) -> None:
        self.setStyleSheet('background-color: #283338')

    def leaveEvent(self, event:QEvent) -> None:
        self.setStyleSheet('background-color: none')
