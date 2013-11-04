__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os

from PyQt4 import QtCore, QtGui


def get_icon(fileName):
    return QtGui.QIcon(os.path.join(QtGui.qApp.appDir, 'icons', fileName))
recent_doc_icon = get_icon('blue-folder-open-document-text.png')


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowIcon(get_icon('nonograms-logo.png'))

        self.boardView = board.BoardView()
        self.setCentralWidget(self.boardView)
        self.statusBar()  # create status bar

        # Create menu
        self.fileMenu = self.menuBar().addMenu('Файл')
        self.actionFileOpen = self.createAction(
            'Открыть...', self.handleFileOpen, QtGui.QKeySequence.Open,
            'folder-open-document-text.png')
        self.addActions(self.fileMenu, (self.actionFileOpen, ))
        self.recentFilesMenu = self.fileMenu.addMenu(
            get_icon('folders-stack.png'), 'Недавние файлы')
        self.recentFilesMenu.aboutToShow.connect(self.updateRecentFiles)
        self.actionFileSave = self.createAction(
            'Сохранить', self.fileSave, QtGui.QKeySequence.Save,
            'disk-black.png')
        self.addActions(self.fileMenu, (
            self.actionFileSave,
            self.createAction('Выход', self.close, 'Ctrl+Q',
                              'cross-button.png')
        ))

        self.helpMenu = self.menuBar().addMenu('Помощь')
        self.addActions(self.helpMenu, [
            self.createAction('О программе', self.showHelpAbout,
                              icon='question-button.png'),
            self.createAction('Как играть', self.showHelpUsage,
                              icon='nonograms-logo.png'),
        ])

        self.setWindowTitle('Японские кроссворды')

        self.fileToolbar = self.addToolBar('File')
        self.fileToolbar.setIconSize(QtCore.QSize(16, 16))
        self.fileToolbar.addAction(self.actionFileOpen)
        self.fileToolbar.addAction(self.actionFileSave)

        self.puzzleToolbar = self.addToolBar('Puzzle')
        self.puzzleToolbar.setIconSize(QtCore.QSize(16, 16))
        self.actionPuzzleClear = self.createAction(
            'Очистить', self.handlePuzzleClear)
        self.puzzleToolbar.addAction(self.actionPuzzleClear)
        self.actionPuzzleSolve = self.createAction(
            'Решить', self.handlePuzzleSolve, icon='nonograms-logo.png')
        self.puzzleToolbar.addAction(self.actionPuzzleSolve)

        self.settings = settings.Settings(self)
        QtCore.QTimer.singleShot(
            0, lambda: self._openFile(self.settings.lastPuzzlePath))

    def closeEvent(self, event):
        self.settings.saveSettings()

    def updateRecentFiles(self, filePath=''):
        recentFiles = self.settings.recentFiles
        # remove from the list deleted files
        for i in range(len(recentFiles) - 1, -1, -1):
            if not os.path.isfile(recentFiles[i]):
                del recentFiles[i]

        if filePath:
            # the function adds a file to recent files list if file name given otherwise updates the menu
            filePath = os.path.abspath(filePath)
            try:
                recentFiles.pop(recentFiles.index(filePath))
            except ValueError:
                pass
            recentFiles.insert(0, filePath)
            del recentFiles[10:]  # keep 10 last files
            return
        menu = self.recentFilesMenu
        menu.clear()
        for file in recentFiles:
            menu.addAction(
                get_icon('blue-folder-open-document-text.png'),
                file, lambda file=file: self._openFile(file))
        if menu.isEmpty():
            noItemsAction = menu.addAction('Пусто')
            noItemsAction.setEnabled(False)

    def handlePuzzleClear(self):
        self.boardView.model().board.clear()

    def handlePuzzleSolve(self):
        board = self.boardView.model().board
        for rowNo in range(board.rowCount):
            self.statusBar().showMessage('Решается строка ' + str(rowNo))
            board.solveRow(rowNo)
        for columnNo in range(board.colCount):
            self.statusBar().showMessage('Решается колонка ' + str(columnNo))
            board.solveColumn(columnNo)
        self.statusBar().clearMessage()

    def handleFileOpen(self):
        filePath = QtGui.QFileDialog.getOpenFileName(
            self, 'Открыть файл', self.settings.lastUsedDirectory,
            '*.nonogram (*.nonogram);;*.nonogram1 (*.nonogram1)')
        if filePath:
            self.settings.lastUsedDirectory = os.path.dirname(filePath)
            self._openFile(filePath)

    def _openFile(self, filePath):
        if filePath.endswith('.nonogram1'):
            self.boardView.model().board.load1(filePath)
        elif filePath.endswith('.nonogram'):
            self.boardView.model().board.load(filePath)
        else:
            return
        puzzle_name = os.path.splitext(os.path.basename(filePath))[0]
        self.setWindowTitle('%s - Японские кроссворды' % puzzle_name)
        self.settings.lastPuzzlePath = filePath
        # add to recent files
        self.updateRecentFiles(filePath)

    def fileSave(self):
        self.boardView.model().board.save()

    def showHelpAbout(self):
        import help
        help.showAboutInfo(self)

    def showHelpUsage(self):
        import help
        help.showUsageInfo(self)

    def createAction(self, text, slot=None, shortcut=None, icon='', tip=None,
                     checkable=False, signal='triggered'):
        #Convenience function to create PyQt actions
        action = QtGui.QAction(text, self)
        if icon:
            action.setIcon(get_icon(icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            getattr(action, signal).connect(slot)
        action.setCheckable(checkable)
        return action

    def addActions(self, menu, actions):
        #Add multiple actions to a menu
        for action in actions:
            if action:
                menu.addAction(action)
            else:
                menu.addSeparator()


import board
import settings
