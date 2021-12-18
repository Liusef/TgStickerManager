from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QDropEvent, QResizeEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView


# Container Class

class CellContainer(QWidget):
    """
    Containers for each widget in the gridview
    """

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

    def set(self, widget):
        """
        Sets the widget inside of the Container
        :param widget: The widget to set it to
        :return: None
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(widget)

    def get(self):
        """
        Gets the widget inside of the container
        :return: The widget inside of the container
        """
        if self.layout().count() == 0: return None
        return self.layout().itemAt(self.layout().count() - 1).widget()

    def clear(self):
        """
        Clears the contents of the container
        :return: None
        """
        self.setLayout(QVBoxLayout())


# Main GridView Class

class GridView(QTableView):
    """
    A GridView for showing clickable widgets
    """

    def __init__(self, max_cols: int,
                 cell_height: int = 100, cell_width: int = 100,
                 allow_move: bool = True):
        """
        Instantiates a GridView object
        :param max_cols: Maximum number of columns to show in the gridview
        :param cell_height: The height of each cell in pixels
        :param cell_width: The width of each cell in pixels
        :param allow_move: Allow the user to drag and drop widgets to move them
        """
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
        self.__add_containers()  # Ensuring that all spots on grid have a container
        self.__adjust_dim()  # Adjusting the dimensions of the grid to match number of elements
        self.__set_widget_size()  # Sets the size of the widget

    # Functions for external use

    def append(self, widget: QWidget):
        """
        Appends a widget to the end of the list
        :param widget: The widget to append
        :return: None
        """
        count: int = self.count()
        if self.cols() == 0: self.__append_col()  # Checks if there are no columns to prevent divide by zero exceptions
        if count % self.cols() == 0:  self.__append_row()  # Checks if the last row is full, then add row if needed
        self.set_at_idx(count, widget)  # Add Widget
        self.__adjust_dim()  # Final Adjustments
        self.__set_widget_size()

    def delete(self, idx: int):
        """
        Deletes a widget at a given index
        :param idx: The index to delete at
        :return: None
        """
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
        self.__adjust_dim()  # Final Adjustments
        self.__set_widget_size()

    def count(self) -> int:
        """
        Counts the number of elements in the GridView

        PLEASE NOTE This method DOES NOT RUN in constant time

        :return: The number of elements in the GridView
        """
        i = 0
        while True:  # Loop through grid until you hit a None object
            if self.get_at_idx(i) is None:
                return i
            i += 1

    def set_contents(self, nc: list[QWidget]):
        """
        Sets the contents of the list to a given list of widgets
        :param nc: The list of widgets to set the contents to
        :return: None
        """
        for i in range(self.count()):
            self.delete(0)
        for q in nc:
            self.append(q)

    def get_widget_array(self) -> list[QWidget]:
        """
        Gets a list of all widgets in the GridView in order
        :return: A list of all widgets in the GridView in order
        """
        lst = []
        for i in range(self.count()):
            lst.append(self.get_at_idx(i))
        return lst

    # Basic Getters

    def rows(self) -> int:
        """
        Returns the number of rows
        :return: the number of rows
        """
        return self.model().rowCount()

    def cols(self) -> int:
        """
        Returns the number of columns
        :return: the number of columns
        """
        return self.model().columnCount()

    # Advanced Getters (Require calculation)

    def get_idx(self, row: int, col: int) -> int:
        """
        Converts row and column to index
        :param row: The row
        :param col: The column
        :return: The index
        """
        return row * self.cols() + col

    def get_row(self, idx: int) -> int:
        """
        Converts index to row
        :param idx: The index
        :return: The row
        """
        return 0 if self.cols() == 0 else idx // self.cols()

    def get_col(self, idx: int) -> int:
        """
        Converts the index to column
        :param idx: The index
        :return: The column
        """
        return 0 if self.cols() == 0 else idx % self.cols()

    # Item Getters and Setters

    def get_at_pos(self, row: int, col: int) -> Union[QWidget, None]:
        """
        Returns the widget at a given row/col position
        :param row: The row
        :param col: The column
        :return: The Widget at the given index
        """
        var = self.indexWidget(self.model().index(row, col))
        if isinstance(var, CellContainer): return var.get()
        return None

    def get_at_idx(self, idx: int) -> Union[QWidget, None]:
        """
        Returns the widget at a given index
        :param idx: The index
        :return: The Widget at the given index
        """
        return self.get_at_pos(self.get_row(idx), self.get_col(idx))

    def set_at_pos(self, row: int, col: int, widget: QWidget):
        """
        Sets the cell at a given row/col position to a given widget
        :param row: The row
        :param col: The column
        :param widget: The widget to set the cell to
        :return: None
        """
        self.indexWidget(self.model().index(row, col)).set(widget)

    def set_at_idx(self, idx: int, widget: QWidget):
        """
        Sets the cell at a given index to a given widget
        :param idx: The index
        :param widget: The widget to set the cell to
        :return: None
        """
        self.set_at_pos(self.get_row(idx), self.get_col(idx), widget)

    def set_allow_move(self, allow_move: bool):
        """
        Set whether items can be moved or not
        :param allow_move: Whether items can be moved
        :return: None
        """
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
            if allow_move
            else QAbstractItemView.SelectionMode.NoSelection
        )

    # Modify Row and Column Count

    def __append_row(self):
        """
        Adds a row to the GridView
        :return: None
        """
        self.model().insertRow(self.rows())
        for i in range(self.cols()): self.setIndexWidget(self.model().index(self.rows() - 1, i), CellContainer())

    def __append_col(self):
        """
        Adds a column to the GridView
        :return: None
        """
        self.model().insertColumn(self.cols())
        for i in range(self.rows()): self.setIndexWidget(self.model().index(self.cols() - 1, i), CellContainer())

    def __delete_row(self, idx: int = -1):
        """
        Deletes the row at a given index (or the last row)
        :param idx: The index of the row to delete (Default is -1, if -1 delete the last row)
        :return: None
        """
        self.model().removeRow((self.rows() - 1) if idx == -1 else idx)  # if idx == -1 then delete the last row

    def __delete_col(self, idx: int = -1):
        """
        Deletes the column at a given index (or the last column)
        :param idx: The index of the column to delete (Default is -1, if -1 delete the last row)
        :return: None
        """
        self.model().removeColumn((self.cols() - 1) if idx == -1 else idx)  # if idx == -1 then delete the last col

    # Move and Shift Items in Grid

    def move_widget(self, start: int, end: int):
        """
        Move a widget between positions
        :param start: The start index
        :param end: The end index
        :return: None
        """
        if end > start:
            self.__move_after(start, end)
        elif start > end:
            self.__move_before(start, end)

    def __move_after(self, start: int, end: int):
        """
        Moves a widget to a greater index
        :param start: The starting (lesser) index
        :param end: The ending (greater) index
        :return: None
        """
        elems = []
        for i in range(start + 1, end + 1):
            elems.append(self.get_at_idx(i))
        elems.append(self.get_at_idx(start))
        i = start
        for e in elems:
            self.set_at_idx(i, e)
            i += 1

    def __move_before(self, start: int, end: int):
        """
        Moves a widget to a lesser index
        :param start: The starting (greater) index
        :param end: The ending (lesser) index
        :return: None
        """
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
        self.__set_widget_size()  # Final Adjustments

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.__set_widget_size()

    # Internal QoL methods

    def __add_containers(self):
        """
        Adds CellContainers to GridView cells that don't already have one
        :return: None
        """
        for i in range(self.rows()):
            for j in range(self.cols()):
                if self.indexWidget(self.model().index(i, j)) is None:
                    self.setIndexWidget(self.model().index(i, j), CellContainer())  # Adds but doesn't replace cells

    def __adjust_dim(self):
        """
        Automatically adjusts the dimensions of the GridView to center cells as best as possible
        :return: None
        """
        count: int = self.count()
        cols: int = count
        cols = self.max_cols if cols > self.max_cols else cols
        cols = 1 if cols < 0 else cols  # The actual number of columns
        a_cols = 1 if cols == 0 else cols  # The number of colums that is greater than 0 (for division)
        elems = self.get_widget_array()
        if cols > self.cols():  # Adds columns until appropriate
            while cols > self.cols():
                self.__append_col()
        elif cols < self.cols():  # Removes columns until appropriate
            while cols < self.cols():
                self.__delete_col()
        rows: int = count // a_cols
        rows = rows if count % a_cols == 0 else rows + 1  # Row count
        if rows > self.rows():  # Adds rows until appropriate
            while rows > self.rows():
                self.__append_row()
        elif rows < self.rows():  # Removes rows until appropriate
            while rows < self.rows():
                self.__delete_row()
        self.__add_containers()  # Adds containers to all cells if they aren't there
        for i in range(len(elems)):
            self.set_at_idx(i, elems[i])  # Replaces widgets in the order they were aleady there
        self.setFixedWidth(a_cols * self.cell_width + 4)  # Sets the width of the widget according to number of columns

    def __set_widget_size(self):
        """
        Sets the size of the GridView widget according to whether there needs to be a scrollbar
        :return: None
        """
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
    """
    Generates a GridView with a list of QWidgets
    :param widgets: The list of widgets to include in the GridView
    :param max_cols: The maximum number of columns in the GridView
    :param cell_height: The height of cells in px
    :param cell_width: The width of cells in px
    :param allow_move: Whether to allow the user to drag and drop move widgets
    :return: A GridView with the list of QWidgets and properties specified
    """
    gridview: GridView = GridView(max_cols, cell_height, cell_width, allow_move)
    for w in widgets:
        gridview.append(w)
    return gridview
