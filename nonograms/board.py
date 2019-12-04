import os
import itertools

from PyQt5 import QtCore, QtGui, QtWidgets


from .solver import PLACEHOLDER, FILLED, BLANK, solve_line


class Board():
    """
    """
    def __init__(self, model):
        self.model = model
        self.row_numbers = []
        self.col_numbers = []
        self.data = []
        self.file_path = None
        self.clear()

    @property
    def row_count(self):
        return len(self.row_numbers)

    @property
    def col_count(self):
        return len(self.col_numbers)

    @property
    def max_row_num_count(self):
        return len(self.row_numbers[0]) if self.row_numbers else 0

    @property
    def max_col_num_count(self):
        return len(self.col_numbers[0]) if self.col_numbers else 0

    def clear(self):
        self.model.layoutAboutToBeChanged.emit()
        self.data = [[PLACEHOLDER] * self.col_count for _ in range(self.row_count)]
        self.model.layoutChanged.emit()

    def set_data(self, row, column, state):
        self.data[row][column] = state
        index = self.model.index(
            row + self.max_col_num_count, column + self.max_row_num_count)
        self.model.dataChanged.emit(index, index)

    def get_numbers(self, line):
        numbers = []
        for state, block in itertools.groupby(line):
            if state == FILLED:
                block_length = sum(1 for _ in block)
                numbers.append(block_length)
            elif state == BLANK:
                pass
            else:
                raise TypeError('Invalid cell value: %r' % state)
        return numbers

    def load(self, file_path):
        """
        """
        if not os.path.isfile(file_path):
            return
        with open(file_path) as file:
            board = file.read().splitlines()

        row_numbers = [self.get_numbers(row) for row in board]

        col_numbers = [self.get_numbers([row[col_no] for row in board])
                      for col_no in range(len(board[0]))]

        maxRowNumCount = max(map(len, row_numbers))
        self.row_numbers = [
            [0] * (maxRowNumCount - len(_row_numbers)) + _row_numbers
            for _row_numbers in row_numbers
        ]
        max_col_num_count = max(map(len, col_numbers))
        self.col_numbers = [
            [0] * (max_col_num_count - len(_col_numbers)) + _col_numbers
            for _col_numbers in col_numbers
        ]
        self.clear()

        self.file_path = file_path

    def load1(self, file_path):
        # загрузить файл с цифрами как здесь:
        # http://www.bestcrosswords.ru/jp/20003009-form.html
        if not os.path.isfile(file_path):
            return
        with open(file_path,) as file:
            section_no = 0
            vertical_numbers_lines = []
            horizontal_numbers_lines = []
            for line in file:
                line = line.strip()
                if line:
                    if section_no == 0:
                        vertical_numbers_lines.append(map(int, line.split()))
                    elif section_no == 1:
                        horizontal_numbers_lines.append(map(int, line.split()))
                else:
                    section_no += 1

        self.row_numbers = list(zip(*horizontal_numbers_lines))
        self.col_numbers = list(zip(*vertical_numbers_lines))
        self.clear()

        self.file_path = file_path

    def solve_row(self, row_no):
        numbers = filter(None, self.row_numbers[row_no])
        line = solve_line(self.data[row_no], numbers)
        for col_no, state in enumerate(line):
            self.set_data(row_no, col_no, state)

    def solveColumn(self, col_no):
        numbers = filter(None, self.col_numbers[col_no])
        line = solve_line([row[col_no] for row in self.data], numbers)
        for rowNo, state in enumerate(line):
            self.set_data(rowNo, col_no, state)

    def save(self):
        for row in self.data:
            for state in row:
                if state not in (FILLED, BLANK):
                    raise Exception('The puzzle is not yet solved!')
        filePath = os.path.splitext(self.file_path)[0] + '.nonogram'
        with open(filePath, 'w', encoding='utf8') as file:
            for line in self.data:
                file.write(''.join(line) + '\n')


class BoardView(QtWidgets.QTableView):
    """
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setModel(BoardModel(self))
        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        self.item_delegate = BoardViewItemDelegate(self)
        self.setItemDelegate(self.item_delegate)

        self.setShowGrid(False)
        #self.setFocusPolicy(QtCore.Qt.NoFocus)

        #self.setStyleSheet('font: 10pt "Courier New"')

        self.viewport().installEventFilter(self)

        self.init_view(22)  # default cell size

    def init_view(self, cell_size):
        self.current_action = None
        self.cell_size = cell_size
        self.verticalHeader().setDefaultSectionSize(cell_size)
        self.horizontalHeader().setDefaultSectionSize(cell_size)
        for row_no in range(self.verticalHeader().count()):
            self.setRowHeight(row_no, cell_size)
        for column_no in range(self.horizontalHeader().count()):
            self.setColumnWidth(column_no, cell_size)

        numbers_font = QtWidgets.QApplication.font()
        fm = QtGui.QFontMetrics(numbers_font)
        # рассчитываем, что в числах не будет больше 2 цифр
        factor = (cell_size - 6) / fm.width('99')
        if factor < 1 or factor > 1.25:
            numbers_font.setPointSizeF(numbers_font.pointSizeF() * factor)

        self.setFont(numbers_font)

    def switch_cell(self, mouse_event, state=None):
        board = self.model().board
        row = self.rowAt(mouse_event.y())
        column = self.columnAt(mouse_event.x())
        board_row = row - board.max_col_num_count
        board_column = column - board.max_row_num_count

        if board_row < 0 or board_column < 0:
            return

        if state is None:
            if self.current_action is None:
                return
            state = self.current_action
        else:
            if state == board.data[board_row][board_column]:
                state = PLACEHOLDER
            self.current_action = state
        board.set_data(board_row, board_column, state)

    def eventFilter(self, target, event):  # target - viewport

        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() == QtCore.Qt.LeftButton:
                model = self.model()
                row_no = self.rowAt(event.y()) - model.board.max_col_num_count
                col_no = self.columnAt(event.x()) - model.board.max_row_num_count
                if row_no < 0 and col_no < 0:
                    QtWidgets.qApp.mainWindow.handlePuzzleSolve()
                else:
                    if col_no < 0:
                        model.board.solve_row(row_no)
                    elif row_no < 0:
                        model.board.solveColumn(col_no)
                return True
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                # LeftClick -> box; Shift + LeftClick -> space
                state = (BLANK if event.modifiers() == QtCore.Qt.ShiftModifier
                         else FILLED)
                self.switch_cell(event, state)
                return True
            elif event.button() == QtCore.Qt.RightButton:
                model = self.model()
                row_no = self.rowAt(event.y()) - model.board.max_col_num_count
                col_no = self.columnAt(event.x()) - model.board.max_row_num_count
                if row_no >= 0 and col_no >= 0:
                    self.switch_cell(event, BLANK)  # RightClick -> space
                return True
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.buttons() == QtCore.Qt.NoButton:
                self.current_action = None
            return True
        elif event.type() == QtCore.QEvent.MouseMove:
            self.switch_cell(event)
            return True
        elif event.type() == QtCore.QEvent.Wheel:
            # zoom board
            if event.modifiers() == QtCore.Qt.ControlModifier:
                cell_size = self.cell_size + int(event.angleDelta().y())
                if cell_size > 10:  # минимальный размер ячейки
                    self.init_view(cell_size)
                return True

        # standard event processing
        return super().eventFilter(target, event)


class BoardViewItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.numbers_brush = QtGui.QBrush(QtGui.QColor(211, 211, 211))
        self.border_pen = QtGui.QPen(QtGui.QColor(211, 211, 211))
        self.box_brush = QtGui.QBrush(QtGui.QColor(80, 80, 80))
        self.cell_brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        self.numbers_pen = QtGui.QPen(QtCore.Qt.black)
        self.numbers_border_pen = QtGui.QPen(QtGui.QColor(136, 136, 136))
        self.space_pen = QtGui.QPen(QtCore.Qt.gray)
        self.space_brush = QtGui.QBrush(QtCore.Qt.white)

    def paint(self, painter, option, index,
              render_hint=QtGui.QPainter.TextAntialiasing|QtGui.QPainter.HighQualityAntialiasing):
        painter.setRenderHints(render_hint)
        model = index.model()
        board = model.board
        row = index.row()
        column = index.column()
        board_row = row - board.max_col_num_count
        board_column = column - board.max_row_num_count

        if board_row < 0 and board_column < 0:
            painter.fillRect(option.rect, self.cell_brush)
            return
        if board_row < 0:
            # это ячейка зоны чисел колонок
            number = board.col_numbers[board_column][row]
            self.draw_number(
                painter, option.rect, number, board_row, board_column)
        elif board_column < 0:
            # это ячейка зоны чисел строк
            number = board.row_numbers[board_row][column]
            self.draw_number(
                painter, option.rect, number, board_row, board_column)
        else:
            # это ячейка поля
            cell_value = board.data[board_row][board_column]
            if cell_value == PLACEHOLDER:
                painter.fillRect(option.rect, self.cell_brush)
            elif cell_value == FILLED:
                self.draw_box(painter, option.rect.adjusted(0, 0, -1, -1))
            elif cell_value == BLANK:
                self.draw_space(painter, option.rect)
            self.draw_borders(painter, option.rect, board_row, board_column)

    def draw_borders(self, painter, rect, row, column):
        pen = self.border_pen
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(rect.topRight(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        # Draw wider border each 5 cells
        pen.setWidth(2)
        painter.setPen(pen)
        if (row + 1) % 5 == 1 and row > 0:
            painter.drawLine(rect.topLeft(), rect.topRight())
        if (column + 1) % 5 == 1 and column > 0:
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

    def draw_box(self, painter, rect):
        """Нарисовать закрашенную ячейку.
        """
        painter.fillRect(rect, self.box_brush)

    def draw_space(self, painter, rect):
        """Нарисовать забеленную ячейку.
        """
        painter.fillRect(rect, self.space_brush)
        painter.setPen(self.space_pen)
        padding = min(rect.width(), rect.height()) / 3
        rect = rect.adjusted(padding, padding, -padding, -padding)
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.topRight())

    def draw_number(self, painter, rect, number, row, column,
                    align=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter):
        painter.fillRect(rect, self.numbers_brush)

        pen = self.numbers_border_pen
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(rect.topRight(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        pen.setWidth(2)
        painter.setPen(pen)
        if (row + 1) % 5 == 1 and row > 0:
            painter.drawLine(rect.topLeft(), rect.topRight())
        if (column + 1) % 5 == 1 and column > 0:
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

        if number:
            painter.setPen(self.numbers_pen)
            rect = rect.adjusted(0, 0, -3, 0)
            painter.drawText(rect, align, str(number))


class BoardModel(QtCore.QAbstractTableModel):

    def __init__(self, parent):
        super().__init__(parent)
        self.board = Board(self)

    def rowCount(self, parent_index):
        return self.board.row_count + self.board.max_col_num_count

    def columnCount(self, parent_index):
        return self.board.col_count + self.board.max_row_num_count

    def getCellValue(self, index):
        return self.board.data[index.row()][index.column()]

    def data(self, index, role):
        return None
