__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os
import itertools

from PyQt4 import QtCore, QtGui


PLACEHOLDER, FILLED, BLANK = ' @.'


class Board():
    """
    """
    def __init__(self, model):
        self.model = model
        self.rowNumbers = []
        self.colNumbers = []
        self.data = []
        self.solver = solver.Solver()
        self.filePath = None
        self.clear()

    @property
    def rowCount(self):
        return len(self.rowNumbers)

    @property
    def colCount(self):
        return len(self.colNumbers)

    @property
    def maxRowNumCount(self):
        return len(self.rowNumbers[0]) if self.rowNumbers else 0

    @property
    def maxColNumCount(self):
        return len(self.colNumbers[0]) if self.colNumbers else 0

    def clear(self):
        self.model.layoutAboutToBeChanged.emit()
        self.data = [[PLACEHOLDER] * self.colCount for _ in range(self.rowCount)]
        self.model.layoutChanged.emit()

    def setData(self, row, column, state):
        self.data[row][column] = state
        index = self.model.index(
            row + self.maxColNumCount, column + self.maxRowNumCount)
        self.model.dataChanged.emit(index, index)

    def getNumbers(self, line):
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

    def load(self, filePath):
        """
        """
        if not os.path.isfile(filePath):
            return
        with open(filePath, 'r', encoding='utf8') as file:
            board = file.read().splitlines()

        rowNumbers = [self.getNumbers(row) for row in board]

        colNumbers = [self.getNumbers([row[colNo] for row in board])
                      for colNo in range(len(board[0]))]

        maxRowNumCount = max(map(len, rowNumbers))
        self.rowNumbers = [
            [0] * (maxRowNumCount - len(_rowNumbers)) + _rowNumbers
            for _rowNumbers in rowNumbers
        ]
        maxColNumCount = max(map(len, colNumbers))
        self.colNumbers = [
            [0] * (maxColNumCount - len(_colNumbers)) + _colNumbers
            for _colNumbers in colNumbers
        ]
        self.clear()

        self.filePath = filePath

    def load1(self, filePath):
        # загрузить файл с цифрами как здесь:
        # http://www.bestcrosswords.ru/jp/20003009-form.html
        if not os.path.isfile(filePath):
            return
        with open(filePath, 'r', encoding='utf8') as file:
            sectionNo = 0
            verticalNumbersLines = []
            horizontalNumbersLines = []
            for line in file:
                line = line.strip()
                if line:
                    if sectionNo == 0:
                        verticalNumbersLines.append(map(int, line.split()))
                    elif sectionNo == 1:
                        horizontalNumbersLines.append(map(int, line.split()))
                else:
                    sectionNo += 1

        self.rowNumbers = list(zip(*horizontalNumbersLines))
        self.colNumbers = list(zip(*verticalNumbersLines))
        self.clear()

        self.filePath = filePath

    def solveRow(self, rowNo):
        numbers = filter(None, self.rowNumbers[rowNo])
        line = self.data[rowNo]
        line = self.solver.scanLine(line, numbers)
        for colNo, state in enumerate(line):
            self.setData(rowNo, colNo, state)

    def solveColumn(self, colNo):
        numbers = filter(None, self.colNumbers[colNo])
        line = [row[colNo] for row in self.data]
        line = self.solver.scanLine(line, numbers)
        for rowNo, state in enumerate(line):
            self.setData(rowNo, colNo, state)

    def save(self):
        for row in self.data:
            for state in row:
                if state not in (FILLED, BLANK):
                    raise Exception('The puzzle is not yet solved!')
        filePath = os.path.splitext(self.filePath)[0] + '.nonogram'
        with open(filePath, 'w', encoding='utf8') as file:
            for line in self.data:
                file.write(''.join(line) + '\n')


class BoardView(QtGui.QTableView):
    """
    """
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)

        self.setModel(BoardModel(self))
        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        self.itemDelegate = BoardViewItemDelegate(self)
        self.setItemDelegate(self.itemDelegate)

        self.setShowGrid(False)
        #self.setFocusPolicy(QtCore.Qt.NoFocus)

        #self.setStyleSheet('font: 10pt "Courier New"')

        self.viewport().installEventFilter(self)

        self.initView(22)  # default cell size

    def initView(self, cellSize):
        self.currentAction = None
        self.cellSize = cellSize
        self.verticalHeader().setDefaultSectionSize(cellSize)
        self.horizontalHeader().setDefaultSectionSize(cellSize)
        for rowNo in range(self.verticalHeader().count()):
            self.setRowHeight(rowNo, cellSize)
        for columnNo in range(self.horizontalHeader().count()):
            self.setColumnWidth(columnNo, cellSize)

        numbersFont = QtGui.QApplication.font()
        fm = QtGui.QFontMetrics(numbersFont)
        # рассчитываем, что в числах не будет больше 2 цифр
        factor = (cellSize - 6) / fm.width('99')
        if factor < 1 or factor > 1.25:
            numbersFont.setPointSizeF(numbersFont.pointSizeF() * factor)

        self.setFont(numbersFont)

        self.borderPen = QtGui.QPen(QtGui.QColor(211, 211, 211))
        self.boxBrush = QtGui.QBrush(QtGui.QColor(80, 80, 80))
        self.spacePen = QtGui.QPen(QtCore.Qt.gray)
        self.spaceBrush = QtGui.QBrush(QtCore.Qt.white)
        self.cellBrush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        self.numbersBrush = QtGui.QBrush(QtGui.QColor(211, 211, 211))
        self.numbersPen = QtGui.QPen(QtCore.Qt.black)
        self.numbersBorderPen = QtGui.QPen(QtGui.QColor(136, 136, 136))

    def switchCell(self, mouseEvent, state=None):
        board = self.model().board
        row = self.rowAt(mouseEvent.y())
        column = self.columnAt(mouseEvent.x())
        boardRow = row - board.maxColNumCount
        boardColumn = column - board.maxRowNumCount

        if boardRow < 0 or boardColumn < 0:
            return

        if state is None:
            if self.currentAction is None:
                return
            state = self.currentAction
        else:
            if state == board.data[boardRow][boardColumn]:
                state = PLACEHOLDER
            self.currentAction = state
        board.setData(boardRow, boardColumn, state)

    def eventFilter(self, target, event):  # target - viewport

        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                # LeftClick -> box; Shift + LeftClick -> space
                state = (BLANK if event.modifiers() == QtCore.Qt.ShiftModifier
                         else FILLED)
                self.switchCell(event, state)
                return True
            elif event.button() == QtCore.Qt.RightButton:
                model = self.model()
                rowNo = self.rowAt(event.y()) - model.board.maxColNumCount
                colNo = self.columnAt(event.x()) - model.board.maxRowNumCount
                if rowNo >= 0 and colNo >= 0:
                    self.switchCell(event, BLANK)  # RightClick -> space
                elif rowNo >= 0 or colNo >= 0:
                    if colNo < 0:
                        model.board.solveRow(rowNo)
                    elif rowNo < 0:
                        model.board.solveColumn(colNo)
                else:
                    QtGui.qApp.mainWindow.handlePuzzleSolve()
                return True
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.buttons() == QtCore.Qt.NoButton:
                self.currentAction = None
            return True
        elif event.type() == QtCore.QEvent.MouseMove:
            self.switchCell(event)
            return True
        elif event.type() == QtCore.QEvent.Wheel:
            # zoom board
            if event.modifiers() == QtCore.Qt.ControlModifier:
                cellSize = self.cellSize + int(event.delta() / 120)
                if cellSize > 10:  # минимальный размер ячейки
                    self.initView(cellSize)
                return True

        # standard event processing
        return super().eventFilter(target, event)


class BoardViewItemDelegate(QtGui.QStyledItemDelegate):
    """
    """
    def paint(self, painter, option, index,
              renderHint=QtGui.QPainter.TextAntialiasing):
        painter.setRenderHint(renderHint)
        model = index.model()
        board = model.board
        row = index.row()
        column = index.column()
        boardRow = row - board.maxColNumCount
        boardColumn = column - board.maxRowNumCount

        if boardRow < 0 and boardColumn < 0:
            painter.fillRect(option.rect, self.parent().numbersBrush)
            return
        if boardRow < 0:
            # это ячейка зоны чисел колонок
            number = board.colNumbers[boardColumn][row]
            self.drawNumber(
                painter, option.rect, number, boardRow, boardColumn)
        elif boardColumn < 0:
                # это ячейка зоны чисел строк
            number = board.rowNumbers[boardRow][column]
            self.drawNumber(
                painter, option.rect, number, boardRow, boardColumn)
        else:
            # это ячейка поля
            cellValue = board.data[boardRow][boardColumn]
            if cellValue == PLACEHOLDER:
                self.drawCell(painter, option.rect)
            elif cellValue == FILLED:
                self.drawBox(painter, option.rect)
            elif cellValue == BLANK:
                self.drawSpace(painter, option.rect)
            self.drawBorders(painter, option.rect, boardRow, boardColumn)

    def drawCell(self, painter, rect):
        """Нарисовать обычную нерешенную ячейку.
        """
        painter.fillRect(rect, self.parent().cellBrush)

    def drawBorders(self, painter, rect, row, column):
        pen = self.parent().borderPen
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(rect.topRight(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        rect = rect.adjusted(1, 1, 0, 0)
        pen.setWidth(2)
        painter.setPen(pen)
        if (row + 1) % 5 == 1 and row > 0:
            painter.drawLine(rect.topLeft(), rect.topRight())
        if (column + 1) % 5 == 1 and column > 0:
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

    def drawBox(self, painter, rect):
        """Нарисовать закрашенную ячейку.
        """
        painter.fillRect(rect, self.parent().boxBrush)

    def drawSpace(self, painter, rect):
        """Нарисовать забеленную ячейку.
        """
        painter.fillRect(rect, self.parent().spaceBrush)
        painter.setPen(self.parent().spacePen)
        padding = min(rect.width(), rect.height()) / 3
        rect = rect.adjusted(padding, padding, -padding, -padding)
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.topRight())

    def drawNumber(self, painter, rect, number, row, column,
                   align=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter):
        painter.fillRect(rect, self.parent().numbersBrush)

        pen = self.parent().numbersBorderPen
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(rect.topRight(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        rect = rect.adjusted(1, 1, 0, 0)
        pen.setWidth(2)
        painter.setPen(pen)
        if (row + 1) % 5 == 1 and row > 0:
            painter.drawLine(rect.topLeft(), rect.topRight())
        if (column + 1) % 5 == 1 and column > 0:
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

        if number:
            painter.setPen(self.parent().numbersPen)
            rect = rect.adjusted(0, 0, -3, 0)
            painter.drawText(rect, align, str(number))


class BoardModel(QtCore.QAbstractTableModel):

    def __init__(self, parent):
        super().__init__(parent)
        self.board = Board(self)

    def rowCount(self, parentIndex):
        return self.board.rowCount + self.board.maxColNumCount

    def columnCount(self, parentIndex):
        return self.board.colCount + self.board.maxRowNumCount

    def getCellValue(self, index):
        return self.board.data[index.row()][index.column()]

    def data(self, index, role):
        return None


from . import solver
