from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QDropEvent, QResizeEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView


# TODO Write Docstrings for all of these

# Container Class

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


# Main GridView Class

class GridView(QTableView):
    def __init__(self, max_cols: int,
                 cell_height: int = 100, cell_width: int = 100,
                 allow_move: bool = True):
        super().__init__()

        # Set fields

        self.cell_width = cell_width
        self.cell_height = cell_height
        self.max_cols = max_cols

        # Set properties for Headers

        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        vh = self.verticalHeader()
        hh = self.horizontalHeader()
        vh.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        vh.setDefaultSectionSize(self.cell_height)
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        hh.setDefaultSectionSize(self.cell_width)

        # Cosmetics for the grid itself and setting options for drag and drop

        self.setShowGrid(False)
        self.set_allow_move(allow_move)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setModel(QStandardItemModel(1, self.max_cols, self))

        # Scrolling preferences

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setAutoScroll(True)
        self.setAutoScrollMargin(50)

        # Final Adjustments

        self.add_containers()  # Ensuring that all spots on grid have a container
        self.adjust_dim()  # Adjusting the dimensions of the grid to match number of elements
        self.set_widget_size()  # Sets the size of the widget

    # Functions for external use

    def append(self, widget: QWidget):
        count: int = self.count()
        if self.cols() == 0: self.append_col()  # Checks if there are no columns to prevent divide by zero exceptions
        if count % self.cols() == 0:  self.append_row()  # Checks if the last row is full, then add row if needed
        self.set_at_idx(count, widget)  # Add Widget
        self.adjust_dim()  # Final Adjustments
        self.set_widget_size()

    def delete(self, idx: int):
        count: int = self.count()
        elems = []
        if idx >= count: return  # If the input index is invalid, return
        for i in range(idx + 1, count):  # Add all elements after the desired element to delete to list
            elems.append(self.get_at_idx(i))
        i = idx
        for e in elems:  # Shift everything up by one to account for deleted item
            self.set_at_idx(i, e)
        # Delete the last item in the list and replace with empty container
        self.setIndexWidget(self.model().index(self.get_row(count - 1), self.get_col(count - 1)), CellContainer())
        self.adjust_dim() # Final Adjustments
        self.set_widget_size()

    def count(self) -> int:
        i = 0
        while True:  # Loop through grid until you hit a None object
            if self.get_at_idx(i) is None:
                return i
            i += 1

    def get_widget_array(self) -> list[QWidget]:
        lst = []
        for i in range(self.count()):
            lst.append(self.get_at_idx(i))
        return lst

    # Basic Getters

    def rows(self) -> int:
        return self.model().rowCount()

    def cols(self) -> int:
        return self.model().columnCount()

    # Advanced Getters (Require calculation)

    def get_idx(self, row: int, col: int) -> int:
        return row * self.cols() + col

    def get_row(self, idx: int) -> int:
        return 0 if self.cols() == 0 else idx // self.cols()

    def get_col(self, idx: int) -> int:
        return 0 if self.cols() == 0 else idx % self.cols()

    # Item Getters and Setters

    def get_at_pos(self, row: int, col: int) -> Union[QWidget, None]:
        var = self.indexWidget(self.model().index(row, col))
        if isinstance(var, CellContainer): return var.get()
        return None

    def get_at_idx(self, idx: int) -> Union[QWidget, None]:
        return self.get_at_pos(self.get_row(idx), self.get_col(idx))

    def set_at_pos(self, row: int, col: int, widget: QWidget):
        self.indexWidget(self.model().index(row, col)).set(widget)

    def set_at_idx(self, idx: int, widget: QWidget):
        self.set_at_pos(self.get_row(idx), self.get_col(idx), widget)

    def set_allow_move(self, allow_move: bool):
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
            if allow_move
            else QAbstractItemView.SelectionMode.NoSelection
        )

    # Modify Row and Column Count

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

    # Move and Shift Items in Grid

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

    # Qt Event Overrides

    def dropEvent(self, event: QDropEvent) -> None:
        pos = event.pos()
        r = (pos.y() + self.verticalScrollBar().value()) // self.cell_height  # Gets the row accounting for scrolling
        c = pos.x() // self.cell_width  # Gets the column
        if c >= self.cols() or c < 0: return  # If column is not valid return
        start = self.get_idx((self.selectedIndexes()[0]).row(), (self.selectedIndexes()[0]).column())
        end = self.get_idx(r, c)
        if self.get_at_idx(start) is None or self.get_at_idx(end) is None: return  # Check if user selected blank cell
        self.move_widget(start, end)  # Move accordingly
        self.set_widget_size()  # Final Adjustments

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.set_widget_size()

    # Internal QoL methods

    def add_containers(self):
        for i in range(self.rows()):
            for j in range(self.cols()):
                if self.indexWidget(self.model().index(i, j)) is None:
                    self.setIndexWidget(self.model().index(i, j), CellContainer())  # Adds but doesn't replace cells

    def adjust_dim(self):
        count: int = self.count()
        cols: int = count
        cols = self.max_cols if cols > self.max_cols else cols
        cols = 1 if cols < 0 else cols  # The actual number of columns
        a_cols = 1 if cols == 0 else cols  # The number of colums that is greater than 0 (for division)
        elems = self.get_widget_array()
        if cols > self.cols():  # Adds columns until appropriate
            while cols > self.cols():
                self.append_col()
        elif cols < self.cols():  # Removes columns until appropriate
            while cols < self.cols():
                self.delete_col()
        rows: int = count // a_cols
        rows = rows if count % a_cols == 0 else rows + 1  # Row count
        if rows > self.rows():  # Adds rows until appropriate
            while rows > self.rows():
                self.append_row()
        elif rows < self.rows():  # Removes rows until appropriate
            while rows < self.rows():
                self.delete_row()
        self.add_containers()  # Adds containers to all cells if they aren't there
        for i in range(len(elems)):
            self.set_at_idx(i, elems[i])  # Replaces widgets in the order they were aleady there
        self.setFixedWidth(a_cols * self.cell_width + 4)  # Sets the width of the widget according to number of columns

    def set_widget_size(self):
        # Checking if there's a scrollbar, if so, account for width of scrollbar by adding 17px if not alr present
        if self.height() < (self.rows() * self.cell_height + 4) and self.width() % self.cell_width != (4 + 17):
            self.setFixedWidth((self.width() // self.cell_width) * self.cell_width + 4 + 17)
        # Checking if there's no scrollbar, if so, remove scrollbar width if present
        elif self.height() > (self.rows() * self.cell_height + 4) and self.width() % self.cell_width != (4):
            self.setFixedWidth((self.width() // self.cell_width) * self.cell_width + 4)
        # self.setMaximumHeight((self.rows() if self.rows() > 0 else 1) * self.cell_height + 4)


# Static Methods

def generate(widgets: list[QWidget], max_cols: int,
             cell_height: int = 100, cell_width: int = 100,
             allow_move: bool = True) -> GridView:
    gridview: GridView = GridView(max_cols, cell_height, cell_width, allow_move)
    for w in widgets:
        gridview.append(w)
    return gridview
