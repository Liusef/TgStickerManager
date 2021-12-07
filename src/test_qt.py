import asyncio
import importlib.resources as ilr
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
from src.Qt.GridView import GridView
from src.Qt.ClickWidget import ClickWidget


class CellWidget(QWidget):
    def __init__(self, name: str, urmom: str):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)
        self.name = name

        a = QLabel()
        a.setText(name)
        a.setAlignment(Qt.AlignCenter)
        b = QLabel()
        b.setText(urmom)
        b.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(a)
        self.layout().addWidget(b)


def add(wid: GridView):
    cw = CellWidget(f"Richard {wid.count()}", str(random()))
    click = ClickWidget()
    click.setCentralWidget(cw)
    click.clicked.connect(lambda: print(f"hiya"))
    wid.append(click)


def delete(wid: GridView):
    wid.delete(urmom := wid.count() - 1)
    print(urmom)


def main():
    app = QApplication([])
    app.setStyleSheet(ilr.read_text(assets, 'style.qss'))
    widget = QMainWindow()
    widget.setWindowTitle("PLACEHOLDER")
    widget.setCentralWidget(nest := QWidget())
    nest.setLayout(QVBoxLayout())
    nest.layout().setAlignment(Qt.AlignCenter)

    gv = GridView(5, 10)
    n = QWidget()
    n.setLayout(QVBoxLayout())
    n.layout().setAlignment(Qt.AlignCenter)
    n.layout().addWidget(gv)

    add_button = QPushButton()
    add_button.setText("Add")
    add_button.clicked.connect(lambda: add(gv))

    delete_button = QPushButton()
    delete_button.setText("Delete")
    delete_button.clicked.connect(lambda: delete(gv))

    nest.layout().addWidget(n)
    nest.layout().addWidget(add_button)
    nest.layout().addWidget(delete_button)

    widget.resize(900, 600)

    with QEventLoop(app) as loop:
        widget.show()
        asyncio.set_event_loop(loop)
        loop.run_forever()


if __name__ == '__main__':
    main()
