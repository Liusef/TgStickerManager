import asyncio
import importlib.resources as ilr
from types import ModuleType
import logging
from logging import debug, info, warning, error, critical
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout
from qasync import QEventLoop

from src import assets


def get_pixmap(module: ModuleType, resource: str) -> QPixmap:
    pixmap: QPixmap = QPixmap()
    pixmap.loadFromData(ilr.read_binary(module, resource))
    debug(f'Read {resource} from module {str(module)}, loaded into QPixmap')
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


from src.Qt.pages import login


def main():
    debug('src.Qt.gui.main() called')
    app = QApplication([])
    app.setStyleSheet(ilr.read_text(assets, 'style.qss'))
    widget = MainWindow()
    widget.setWindowIcon(QIcon(get_pixmap(assets, "app.png")))
    widget.setWindowTitle("PLACEHOLDER")
    widget.setCentralWidget(login.TgLoginWidget())
    widget.resize(900, 600)

    with QEventLoop(app) as loop:
        widget.show()
        asyncio.set_event_loop(loop)
        debug('QEventLoop set as asyncio event loop, setting loop to run forever...')
        loop.run_forever()

    debug('QEventLoop has stopped')


if __name__ == '__main__':
    main()
