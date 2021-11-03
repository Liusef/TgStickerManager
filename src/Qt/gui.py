import sys
from types import ModuleType

from src import assets
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QStackedWidget, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtCore import Qt
import importlib.resources as ilr
from pages import login
import phonenumbers


def get_pixmap(module: ModuleType, resource: str) -> QPixmap:
    pixmap: QPixmap = QPixmap()
    pixmap.loadFromData(ilr.read_binary(module, resource))
    return pixmap


def generate_font(label, size: int, weight: QFont.Weight = QFont.Normal):
    font = label.font()
    font.setStyleStrategy(QFont.PreferAntialias)
    font.setPointSize(size)
    font.setWeight(weight)
    return font


def nest_widget(widget: QWidget) -> QWidget:
    nwidget = QWidget()
    nwidget.setLayout(QVBoxLayout())
    nwidget.layout().setAlignment(Qt.AlignCenter)
    nwidget.layout().addWidget(widget)
    return nwidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ilr.read_text(assets, 'style.qss'))
    widget = MainWindow()
    widget.setWindowIcon(QIcon(get_pixmap(assets, "app.png")))
    widget.setWindowTitle("PLACEHOLDER")
    widget.setCentralWidget(login.TgLoginWidget())
    widget.show()
    widget.resize(900, 600)
    exit(app.exec())


if __name__ == '__main__':
    main()
