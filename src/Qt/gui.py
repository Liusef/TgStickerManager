import asyncio
import importlib.resources as ilr

from types import ModuleType
import logging
from logging import debug, info, warning, error, critical
from typing import Callable

from PySide6.QtCore import Qt, Signal, QMetaObject
from PySide6.QtGui import QPixmap, QIcon, QFont, QCloseEvent
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QPushButton
from qasync import QEventLoop

from src import assets


def get_pixmap(module: ModuleType, resource: str) -> QPixmap:
    pixmap: QPixmap = QPixmap()
    pixmap.loadFromData(ilr.read_binary(module, resource))
    debug(f'Read {resource} from module {str(module)}, loaded into QPixmap')
    return pixmap

def get_pixmap_from_file(fpath: str) -> QPixmap:
    pixmap: QPixmap = QPixmap()
    pixmap.load(fpath)
    return pixmap


def generate_font(widget, size: int, weight: QFont.Weight = QFont.Normal) -> QFont:
    font = widget.font()
    font.setStyleStrategy(QFont.PreferAntialias)
    font.setPointSize(size)
    font.setWeight(weight)
    return font


def basic_label(text: str, font: QFont = None, alignment = Qt.AlignCenter) -> QLabel:
    ql = QLabel()
    ql.setText(text)
    ql.setAlignment(alignment)
    if font is not None: ql.setFont(font)
    return ql

def nest_widget(widget: QWidget, alignment = Qt.AlignCenter) -> QWidget:
    nwidget = QWidget()
    nwidget.setLayout(QVBoxLayout())
    nwidget.layout().setAlignment(alignment)
    nwidget.layout().addWidget(widget)
    return nwidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def closeEvent(self, event:QCloseEvent) -> None:
        exit(0)


class Loading(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        label = QLabel()
        label.setText("Loading...")
        label.setFont(generate_font(label, 14, QFont.DemiBold))
        label.setAlignment(Qt.AlignCenter)

        self.layout().addWidget(label)


from src.Qt.pages import login


def main():
    debug('src.Qt.gui.main() called')
    app = QApplication([])
    app.setStyleSheet(ilr.read_text(assets, 'style.qss'))
    widget = MainWindow()
    widget.setWindowIcon(QIcon(get_pixmap(assets, "app.png")))
    widget.setWindowTitle("PLACEHOLDER")
    widget.setCentralWidget(login.TgLoginWidget())
    widget.resize(1000, 750)

    with QEventLoop(app) as loop:
        widget.show()
        asyncio.set_event_loop(loop)
        debug('QEventLoop set as asyncio event loop, setting loop to run forever...')
        loop.run_forever()

    debug('QEventLoop has stopped')


if __name__ == '__main__':
    main()
