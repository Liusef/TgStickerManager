from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QDropEvent, QResizeEvent
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
        self.max_cols = cols

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

        self.add_containers()

        self.adjust_dim()
        self.set_widget_size()

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
        return 0 if self.cols() == 0 else idx // self.cols()

    def get_col(self, idx: int) -> int:
        return 0 if self.cols() == 0 else idx % self.cols()

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

    def append_row(self):
        self.model().insertRow(self.rows())
        for i in range(self.cols()): self.setIndexWidget(self.model().index(self.rows() - 1, i), CellContainer())

    def append_col(self):
        self.model().insertColumn(self.cols())
        for i in range(self.rows()): self.setIndexWidget(self.model().index(self.cols() - 1, i), CellContainer())

    def delete_row(self, idx: int = -1):
        self.model().removeRow((self.rows() - 1) if idx == -1 else idx)  # if idx == -1 then delete the last row

    def delete_col(self, idx: int = -1):
        self.model().removeColumn((self.cols() - 1) if idx == -1 else idx)  # if idx == -1 then delete the last col

    def dropEvent(self, event: QDropEvent) -> None:
        pos = event.pos()
        r = (pos.y() + self.verticalScrollBar().value()) // self.cell_height
        c = pos.x() // self.cell_width
        if c >= self.cols(): return
        start = self.get_idx((self.selectedIndexes()[0]).row(), (self.selectedIndexes()[0]).column())
        end = self.get_idx(r, c)
        if self.get_at_idx(start) is None or self.get_at_idx(end) is None: return
        self.move_widget(start, end)
        self.set_widget_size()

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

    def add_containers(self):
        for i in range(self.rows()):
            for j in range(self.cols()):
                if self.indexWidget(self.model().index(i, j)) is None:
                    self.setIndexWidget(self.model().index(i, j), CellContainer())

    def append(self, widget: QWidget):
        count: int = self.count()
        if self.cols() == 0: self.append_col()
        if count % self.cols() == 0:
            self.model().insertRow(self.rows())
            self.add_containers()
        self.set_at_idx(count, widget)
        self.adjust_dim()
        self.set_widget_size()

    def delete(self, idx: int):
        count: int = self.count()
        elems = []
        if idx >= count: return
        for i in range(idx + 1, count):
            elems.append(self.get_at_idx(i))
        i = idx
        for e in elems:
            self.set_at_idx(i, e)
        self.setIndexWidget(self.model().index(self.get_row(count - 1), self.get_col(count - 1)), CellContainer())
        if self.rows() > (count // self.cols() if count % self.cols() == 0 else count // self.cols() + 1):
            self.model().removeRow(self.rows() - 1)
        self.adjust_dim()
        self.set_widget_size()

    def adjust_dim(self):
        count: int = self.count()
        cols: int = count
        cols = self.max_cols if cols > self.max_cols else cols
        cols = 1 if cols < 0 else cols
        a_cols = 1 if cols == 0 else cols
        elems = self.get_widget_array()
        if cols > self.cols():
            while cols > self.cols():
                self.append_col()
        elif cols < self.cols():
            while cols < self.cols():
                self.delete_col()
        rows: int = count // a_cols
        rows = rows if count % a_cols == 0 else rows + 1
        if rows > self.rows():
            while rows > self.rows():
                self.append_row()
        elif rows < self.rows():
            while rows < self.rows():
                self.delete_row()
        self.add_containers()
        for i in range(len(elems)):
            self.set_at_idx(i, elems[i])
        self.setFixedWidth(a_cols * self.cell_width + 4)

    def set_widget_size(self):
        if self.height() < (self.rows() * self.cell_height + 4) and self.width() % self.cell_width != (4 + 17):
            self.setFixedWidth((self.width() // self.cell_width) * self.cell_width + 4 + 17)
        elif self.height() > (self.rows() * self.cell_height + 4) and self.width() % self.cell_width != (4):
            self.setFixedWidth((self.width() // self.cell_width) * self.cell_width + 4)
        # self.setMaximumHeight((self.rows() if self.rows() > 0 else 1) * self.cell_height + 4)

    def resizeEvent(self, event:QResizeEvent) -> None:
        super().resizeEvent(event)
        self.set_widget_size()


def generate(widgets: list[QWidget], cols: int,
             cell_height: int = 100, cell_width: int = 100,
             allow_move: bool = True) -> GridView:
    gridview: GridView = GridView(1, cols, cell_height, cell_width, allow_move)
    for w in widgets:
        gridview.append(w)
    return gridview


