import asyncio
import importlib.resources as ilr
import copy
from random import random
from types import ModuleType
from typing import Union
import logging

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QModelIndex, QPoint
from PySide6.QtGui import QPixmap, QIcon, QFont, QStandardItemModel
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QTableView, QAbstractItemView, \
    QHBoxLayout, QPushButton

from qasync import QEventLoop
from src import assets
from src.Qt import gui
from src.Qt.GridView import GridView
from src.Qt.ClickWidget import ClickWidget, LitClickWidget
from src.Qt.pages.base_sticker import BaseStickerPage
from src.Tg import stickers


def main():
    app = QApplication([])
    app.setStyleSheet(ilr.read_text(assets, 'style.qss'))
    widget = QMainWindow()
    widget.setWindowTitle("PLACEHOLDER")
    widget.setCentralWidget(nest := BaseStickerPage(stickers.deserialize_pack("KaiBlueRoo")))
    nest.setLayout(QVBoxLayout())
    nest.layout().setAlignment(Qt.AlignCenter)

    butt = LitClickWidget()
    butt.setLayout(QVBoxLayout())
    butt.layout().addWidget(gui.basic_label("butt"))
    butt.setFixedSize(100, 64)
    butt.setContentsMargins(0, 0, 0, 0)
    butt.clicked.connect(lambda: print('butt'))

    butt2 = LitClickWidget()
    butt2.setLayout(QVBoxLayout())
    butt2.layout().addWidget(gui.basic_label("richard"))
    butt2.setFixedSize(100, 64)
    butt2.setContentsMargins(0, 0, 0,0 )
    butt2.clicked.connect(lambda: print('richard'))

    butt3 = LitClickWidget()
    butt3.setLayout(QVBoxLayout())
    butt3.layout().addWidget(gui.basic_label("richard"))
    butt3.setFixedSize(100, 64)
    butt3.setContentsMargins(0, 0, 0,0 )
    butt3.clicked.connect(lambda: print('richard'))

    butt4 = LitClickWidget()
    butt4.setLayout(QVBoxLayout())
    butt4.layout().addWidget(gui.basic_label("richard"))
    butt4.setFixedSize(100, 64)
    butt4.setContentsMargins(0, 0, 0,0 )
    butt4.clicked.connect(lambda: print('richard'))

    butt5 = LitClickWidget()
    butt5.setLayout(QVBoxLayout())
    butt5.layout().addWidget(gui.basic_label("richard"))
    butt5.setFixedSize(100, 64)
    butt5.setContentsMargins(0, 0, 0,0 )
    butt5.clicked.connect(lambda: print('richard'))

    butt6 = LitClickWidget()
    butt6.setLayout(QVBoxLayout())
    butt6.layout().addWidget(gui.basic_label("richard"))
    butt6.setFixedSize(100, 64)
    butt6.setContentsMargins(0, 0, 0,0 )
    butt6.clicked.connect(lambda: print('richard'))

    butt7 = LitClickWidget()
    butt7.setLayout(QVBoxLayout())
    butt7.layout().addWidget(gui.basic_label("richard"))
    butt7.setFixedSize(100, 64)
    butt7.setContentsMargins(0, 0, 0,0 )
    butt7.clicked.connect(lambda: print('richard'))

    nest.add_button(butt)
    nest.add_button(butt2)
    nest.add_button(butt3)
    nest.add_button(butt4)
    nest.add_button(butt5)
    nest.add_button(butt6)

    widget.resize(900, 600)

    with QEventLoop(app) as loop:
        widget.show()
        asyncio.set_event_loop(loop)
        loop.run_forever()


if __name__ == '__main__':
    main()
