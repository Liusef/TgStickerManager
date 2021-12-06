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

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setAutoScroll(True)
        self.setAutoScrollMargin(50)

        self.setModel(model := QStandardItemModel(rows, cols, self))

        for i in range(rows):
            for j in range(cols):
                self.setIndexWidget(self.model().index(i, j), CellContainer())
                print(f"i:{i} j:{j}")

        for i in range(rows * cols):
            self.set_at_idx(i, CellWidget("richard", "richard" + str(i)))

        self.append(CellWidget("ree", "ree"))
        self.delete(25)

    def rows(self) -> int:
        return self.model().rowCount()

    def cols(self) -> int:
        return self.model().columnCount()

    def count(self) -> int:
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

    def get_at_pos(self, row: int, col: int) -> Union[CellWidget, None]:
        var = self.indexWidget(self.model().index(row, col))
        if isinstance(var, CellContainer): return var.get()
        return None

    def get_at_idx(self, idx: int) -> Union[CellWidget, None]:
        var = self.indexWidget(self.model().index(self.get_row(idx), self.get_col(idx)))
        if isinstance(var, CellContainer): return var.get()
        return None

    def set_at_pos(self, row: int, col: int, widget: QWidget):
        self.indexWidget(self.model().index(row, col)).set(widget)

    def set_at_idx(self, idx: int, widget: QWidget):
        self.indexWidget(self.model().index(idx // self.cols(), idx % self.cols())).set(widget)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        print(event.pos())
        pos = event.pos()
        r = (pos.y() + self.verticalScrollBar().value()) // self.cellheight
        c = pos.x() // self.cellwidth
        if c >= self.cols(): return
        print(f"r:{r} c:{c}")
        print(self.selectedIndexes())
        start = self.get_idx((self.selectedIndexes()[0]).row(), (self.selectedIndexes()[0]).column())
        end = self.get_idx(r, c)
        if self.get_at_idx(start) is None or self.get_at_idx(end) is None: return
        self.move_widget(start, end)

    def move_widget(self, start: int, end: int):
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

    def append(self, widget: CellWidget):
        count: int = self.count()
        if count % self.cols() == 0:
            self.model().insertRow(self.rows())
            for i in range(self.cols()):
                self.setIndexWidget(self.model().index(self.rows() - 1, i), CellContainer())
        self.set_at_idx(count, widget)

    def delete(self, idx: int):
        elems = []
        if idx >= self.count(): return
        for i in range(idx + 1, self.count()):
            elems.append(self.get_at_idx(i))
        i = idx
        for e in elems:
            self.set_at_idx(i, e)
        if self.rows() > self.count() // self.cols():
            self.model().removeRow(self.rows() - 1)


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
