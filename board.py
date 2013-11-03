__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os

from PyQt4 import QtCore, QtGui


CELL, BOX, SPACE = ' #.'


class BoardView(QtGui.QTableView):
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

    def switchCell(self, mouseEvent, newState=None):
        row = self.rowAt(mouseEvent.y())
        column = self.columnAt(mouseEvent.x())

        model = self.model()
        boardRow = row - model.board.maxColumnBlocks
        boardColumn = column - model.board.maxRowBlocks

        if boardRow < 0 and boardColumn < 0:
            return

        if boardRow >= 0 and boardColumn >= 0:
            if newState is None:
                if self.currentAction is None:
                    return
                newState = self.currentAction
            else:
                if newState == model.board.data[boardRow][boardColumn]:
                    newState = CELL
                else:
                    newState = newState
                self.currentAction = newState
            model.board.setData(boardRow, boardColumn, newState)

    def eventFilter(self, target, event):  # target - viewport

        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                # LeftClick -> box; Shift + LeftClick -> space
                self.switchCell(event, SPACE if event.modifiers() == QtCore.Qt.ShiftModifier else BOX)
                return True
            elif event.button() == QtCore.Qt.RightButton:
                model = self.model()
                boardRow = self.rowAt(event.y()) - model.board.maxColumnBlocks
                boardColumn = self.columnAt(
                    event.x()) - model.board.maxRowBlocks
                if boardRow >= 0 and boardColumn >= 0:
                    self.switchCell(event, SPACE)  # RightClick -> space
                elif boardRow >= 0 or boardColumn >= 0:
                    if boardColumn < 0:
                        model.board.solveRow(boardRow)
                    elif boardRow < 0:
                        model.board.solveColumn(boardColumn)
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
            # board zoom
            if event.modifiers() == QtCore.Qt.ControlModifier:
                cellSize = self.cellSize + int(event.delta() / 120)
                if cellSize > 10:  # минимальный размер ячейки
                    self.initView(cellSize)
                return True

        # standard event processing
        return super().eventFilter(target, event)


class BoardViewItemDelegate(QtGui.QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        model = index.model()
        board = model.board
        row = index.row()
        column = index.column()

        boardRow = row - board.maxColumnBlocks
        boardColumn = column - board.maxRowBlocks

        if row < board.maxColumnBlocks and column < board.maxRowBlocks:
            painter.fillRect(option.rect, self.parent().numbersBrush)
        else:
            if row < board.maxColumnBlocks:  # это ячейка зоны чисел колонок
                number = board.columnsNumbers[boardColumn][row]
                self.drawNumber(painter, option.rect, number, boardRow,
                                boardColumn)
            elif column < board.maxRowBlocks:  # это ячейка зоны чисел строк
                number = board.rowsNumbers[boardRow][column]
                self.drawNumber(painter, option.rect, number, boardRow,
                                boardColumn)
            else:  # это ячейка поля
                cellValue = board.data[boardRow][boardColumn]
                if cellValue == CELL:
                    self.drawCell(painter, option.rect)
                elif cellValue == BOX:
                    self.drawBox(painter, option.rect)
                elif cellValue == SPACE:
                    self.drawSpace(painter, option.rect)
                self.drawBorders(painter, option.rect, boardRow, boardColumn)
        painter.restore()

    def drawCell(self, painter, rect):
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
        painter.fillRect(rect, self.parent().boxBrush)

    def drawSpace(self, painter, rect):
        painter.fillRect(rect, self.parent().spaceBrush)
        painter.setPen(self.parent().spacePen)
        padding = min(rect.width(), rect.height()) / 3
        rect = rect.adjusted(padding, padding, -padding, -padding)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawLine(rect.topLeft(), rect.bottomRight())
        painter.drawLine(rect.bottomLeft(), rect.topRight())
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)

    def drawNumber(self, painter, rect, number, row, column):
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
            painter.drawText(rect,
                             QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
                             str(number))


class Board():
    def __init__(self, model):
        self.model = model
        self.rows = 11
        self.columns = 12
        self.data = [[CELL] * self.columns for i in range(self.rows)]
        self.maxRowBlocks = 0
        self.rowsNumbers = []
        self.maxColumnBlocks = 0
        self.columnsNumbers = []
        self.solver = solver.Solver()

    def setData(self, row, column, newState):
        self.data[row][column] = newState
        index = self.model.index(row + self.maxColumnBlocks,
                                 column + self.maxRowBlocks)
        self.model.dataChanged.emit(index, index)

    def clear(self):
        self.model.layoutAboutToBeChanged.emit()
        self.data = [[CELL] * self.columns for i in range(self.rows)]
        self.model.layoutChanged.emit()

    def load1(self, filePath):
        # загрузить файл с цифрами как здесь:
        # http://www.bestcrosswords.ru/jp/20003009-form.html
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

            self.model.layoutAboutToBeChanged.emit()

            self.rowsNumbers = list(zip(*horizontalNumbersLines))
            self.columnsNumbers = list(zip(*verticalNumbersLines))
            self.maxRowBlocks = len(self.rowsNumbers[0])
            self.maxColumnBlocks = len(self.columnsNumbers[0])
            self.rows = len(self.rowsNumbers)
            self.columns = len(self.columnsNumbers)
            self.data = [[CELL] * self.columns for i in range(self.rows)]

            self.model.layoutChanged.emit()
            self.filePath = filePath

    def solveRow(self, rowNo):
        numbers = [number for number in self.rowsNumbers[rowNo] if number]
        line = self.data[rowNo]
        #print(numbers)
        #print(line)
        line = self.solver.scanLine(line, numbers)
        #print(solver.accumulator, solver.combinations)
        for i in range(len(line)):
            self.setData(rowNo, i, line[i])

    def solveColumn(self, columnNo):
        numbers = [number for number in self.columnsNumbers[columnNo] if
                   number]
        line = [row[columnNo] for row in self.data]
        #print(numbers)
        #print(line)
        line = self.solver.scanLine(line, numbers)
        #print(solver.accumulator, solver.combinations)
        for i in range(len(line)):
            self.setData(i, columnNo, line[i])

    def save(self):
        filePath = os.path.splitext(self.filePath)[0] + '.nonogram'
        with open(filePath, 'w', encoding='utf8') as file:
            for line in self.data:
                file.write(''.join(line) + '\n')
                #sectionNo = 0
                #verticalNumbersLines = []
                #horizontalNumbersLines = []
                #for line in file:
                #line = line.strip()
                #if line:
                #if sectionNo == 0:
                #verticalNumbersLines.append(map(int, line.split()))
                #elif sectionNo == 1:
                #horizontalNumbersLines.append(map(int, line.split()))
                #else:
                #sectionNo += 1
                #
                #self.model.layoutAboutToBeChanged.emit()
                #
                #self.rowsNumbers = list(zip(*horizontalNumbersLines))
                #self.columnsNumbers = list(zip(*verticalNumbersLines))
                #self.maxRowBlocks = len(self.rowsNumbers[0])
                #self.maxColumnBlocks = len(self.columnsNumbers[0])
                #self.rows = len(self.rowsNumbers)
                #self.columns = len(self.columnsNumbers)
                #self.data = []
                #for i in range(self.rows):
                #self.data.append([0] * self.columns)
                #
                #self.model.layoutChanged.emit()


class BoardModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)
        self.board = Board(self)

    def rowCount(self, parent):
        return self.board.rows + self.board.maxColumnBlocks

    def columnCount(self, parent):
        return self.board.columns + self.board.maxRowBlocks

    def getCellValue(self, index):
        return self.board.data[index.row()][index.column()]

    def data(self, index, role):
        return None


import solver
