from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QDropEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView


class CellContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

    def set(self, widget):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(widget)

    def get(self):
        if self.layout().count() == 0: return None
        return self.layout().itemAt(self.layout().count() - 1).widget()

    def clear(self):
        self.setLayout(QVBoxLayout())


class GridView(QTableView):
    def __init__(self, rows: int, cols: int,
                 cell_height: int = 100, cell_width: int = 100,
                 allow_move: bool = True):
        super().__init__()

        self.cell_width = cell_width
        self.cell_height = cell_height

        self.setFixedWidth(cols * self.cell_width + 4 + 17)
        # You have to add 4 pixels to make sure there's not sideways scroll
        # You have to add 17 to account for the vertical scroll bar
        # I hate this so much but i'm not writing a resize event method

        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        vh = self.verticalHeader()
        hh = self.horizontalHeader()
        vh.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        vh.setDefaultSectionSize(self.cell_height)
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        hh.setDefaultSectionSize(self.cell_width)

        self.setShowGrid(False)
        self.set_allow_move(allow_move)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setModel(QStandardItemModel(rows, cols, self))

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setAutoScroll(True)
        self.setAutoScrollMargin(50)

        for i in range(rows):
            for j in range(cols):
                self.setIndexWidget(self.model().index(i, j), CellContainer())

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

    def get_at_pos(self, row: int, col: int) -> Union[QWidget, None]:
        var = self.indexWidget(self.model().index(row, col))
        if isinstance(var, CellContainer): return var.get()
        return None

    def get_at_idx(self, idx: int) -> Union[QWidget, None]:
        var = self.indexWidget(self.model().index(self.get_row(idx), self.get_col(idx)))
        if isinstance(var, CellContainer): return var.get()
        return None

    def set_at_pos(self, row: int, col: int, widget: QWidget):
        self.indexWidget(self.model().index(row, col)).set(widget)

    def set_at_idx(self, idx: int, widget: QWidget):
        self.indexWidget(self.model().index(idx // self.cols(), idx % self.cols())).set(widget)

    def set_allow_move(self, allow_move: bool):
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
            if allow_move
            else QAbstractItemView.SelectionMode.NoSelection
        )

    def dropEvent(self, event: QDropEvent) -> None:
        pos = event.pos()
        r = (pos.y() + self.verticalScrollBar().value()) // self.cell_height
        c = pos.x() // self.cell_width
        if c >= self.cols(): return
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

    def get_widget_array(self) -> list[QWidget]:
        lst = []
        for i in range(self.count()):
            lst.append(self.get_at_idx(i))
        return lst

    def append(self, widget: QWidget):
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


def generate(widgets: list[QWidget], cols: int,
             cell_height: int = 100, cell_width: int = 100,
             allow_move: bool = True) -> GridView:
    gridview: GridView = GridView(1, cols, cell_height, cell_width, allow_move)
    for w in widgets:
        gridview.append(w)
    return gridview


