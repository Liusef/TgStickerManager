import asyncio
import importlib.resources as ilr
from types import ModuleType
from typing import Union
import logging

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QModelIndex, QPoint
from PySide6.QtGui import QPixmap, QIcon, QFont, QStandardItemModel
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QTableView, QAbstractItemView

from qasync import QEventLoop
from src import assets


class CellWidget(QWidget):
    def __init__(self, name: str, urmom: str):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)

        a = QLabel()
        a.setText(name)
        a.setAlignment(Qt.AlignCenter)
        b = QLabel()
        b.setText(urmom)
        b.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(a)
        self.layout().addWidget(b)


class CellContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

    def set(self, qw):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(qw)

    def get(self):
        if self.layout().count() == 0: return None
        return self.layout().itemAt(self.layout().count() - 1).widget()

    def clear(self):
        self.setLayout(QVBoxLayout())


class TestWidget1(QTableView):
    def __init__(self):
        super().__init__()

        self.cellwidth = 100
        self.cellheight = 100
        rows = 5
        cols = 5

        self.setFixedWidth(cols * self.cellwidth + 4 + 17)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        vh = self.verticalHeader()
        hh = self.horizontalHeader()
        vh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        vh.setDefaultSectionSize(self.cellheight)
        hh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        hh.setDefaultSectionSize(self.cellwidth)

        self.setShowGrid(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)

        self.setModel(model := QStandardItemModel(rows, cols, self))

        for i in range(rows):
            for j in range(cols):
                self.setIndexWidget(self.model().index(i, j), CellContainer())

        for i in range(rows * cols):
            self.set_at_idx(i, CellWidget("richard", "richard" + str(i)))

    def rows(self) -> int:
        return self.model().rowCount()

    def cols(self) -> int:
        return self.model().columnCount()

    def count(self):
        i = 0
        while True:
            if self.get_at_idx(i) is None:
                return i
            i += 1

    def get_idx(self, row: int, col: int) -> int:
        return row * self.cols() + col

    def get_row(self, idx: int) -> int:
        return idx // self.cols()

    def get_col(self, idx: int) -> int:
        return idx % self.cols()

    def get_at_pos(self, row: int, col: int) -> QWidget:
        return self.indexWidget(self.model().index(row, col)).get()

    def get_at_idx(self, idx: int):
        return self.indexWidget(self.model().index(idx // self.cols(), idx % self.cols())).get()

    def set_at_pos(self, row: int, col: int, widget: QWidget):
        self.indexWidget(self.model().index(row, col)).set(widget)

    def set_at_idx(self, idx: int, widget: QWidget):
        self.indexWidget(self.model().index(idx // self.cols(), idx % self.cols())).set(widget)

    def dropEvent(self, event:QtGui.QDropEvent) -> None:
        print(event.pos())
        pos = event.pos()
        r = pos.y() // self.cellheight
        c = pos.x() // self.cellwidth
        print(f"r:{r} c:{c}")
        print(self.selectedIndexes())
        start = self.get_idx( (self.selectedIndexes()[0]).row(), (self.selectedIndexes()[0]).column() )
        end = self.get_idx(r, c)
        if end > start:
            self.move_after(start, end)
        elif start > end:
            self.move_before(start, end)

    def move_after(self, start: int, end: int):
        elems = []
        for i in range(start + 1, end + 1):
            elems.append(self.get_at_idx(i))
        elems.append(self.get_at_idx(start))
        i = start
        for e in elems:
            self.set_at_idx(i, e)
            i += 1

    def move_before(self, start: int, end: int):
        elems = [self.get_at_idx(start)]
        for i in range(end, start):
            elems.append(self.get_at_idx(i))
        i = end
        for e in elems:
            self.set_at_idx(i, e)
            i += 1

    def get_widget_array(self) -> list[CellWidget]:
        lst = []
        for i in range(self.count()):
            lst.append(self.get_at_idx(i))
        return lst


def main():
    app = QApplication([])
    app.setStyleSheet(ilr.read_text(assets, 'style.qss'))
    widget = QMainWindow()
    widget.setWindowTitle("PLACEHOLDER")
    widget.setCentralWidget(nest := QWidget())
    nest.setLayout(QVBoxLayout())
    nest.layout().addWidget(TestWidget1())
    nest.layout().setAlignment(Qt.AlignCenter)
    widget.resize(900, 600)

    with QEventLoop(app) as loop:
        widget.show()
        asyncio.set_event_loop(loop)
        loop.run_forever()


if __name__ == '__main__':
    main()
