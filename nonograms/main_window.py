import os

from PyQt5 import QtCore, QtGui, QtWidgets


def get_icon(file_name):
    return QtGui.QIcon(os.path.join(QtWidgets.qApp.appDir, 'icons', file_name))


recent_doc_icon = get_icon('blue-folder-open-document-text.png')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowIcon(get_icon('nonograms-logo.png'))

        self.board_view = board.BoardView()
        self.setCentralWidget(self.board_view)
        self.statusBar()  # create status bar

        # Create menu
        self.file_menu = self.menuBar().addMenu('Файл')
        self.action_file_open = self.createAction(
            'Открыть...', self.handleFileOpen, QtGui.QKeySequence.Open,
            'folder-open-document-text.png')
        self.addActions(self.file_menu, (self.action_file_open,))
        self.recent_files_menu = self.file_menu.addMenu(
            get_icon('folders-stack.png'), 'Недавние файлы')
        self.recent_files_menu.aboutToShow.connect(self.update_recent_files)
        self.action_file_save = self.createAction(
            'Сохранить', self.fileSave, QtGui.QKeySequence.Save,
            'disk-black.png')
        self.addActions(self.file_menu, (
            self.action_file_save,
            self.createAction('Выход', self.close, 'Ctrl+Q',
                              'cross-button.png')
        ))

        self.help_menu = self.menuBar().addMenu('Помощь')
        self.addActions(self.help_menu, [
            self.createAction('О программе', self.show_help_about,
                              icon='question-button.png'),
            self.createAction('Как играть', self.show_help_usage,
                              icon='nonograms-logo.png'),
        ])

        self.setWindowTitle('Японские кроссворды')

        self.file_toolbar = self.addToolBar('File')
        self.file_toolbar.setObjectName('fileToolbar')
        self.file_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.file_toolbar.addAction(self.action_file_open)
        self.file_toolbar.addAction(self.action_file_save)

        self.puzzle_toolbar = self.addToolBar('Puzzle')
        self.puzzle_toolbar.setObjectName('puzzleToolbar')
        self.puzzle_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.action_puzzle_clear = self.createAction(
            'Очистить', self.handle_puzzle_clear)
        self.puzzle_toolbar.addAction(self.action_puzzle_clear)
        self.action_puzzle_solve = self.createAction(
            'Решить', self.handlePuzzleSolve, icon='nonograms-logo.png')
        self.puzzle_toolbar.addAction(self.action_puzzle_solve)

        self.settings = settings.Settings(self)
        QtCore.QTimer.singleShot(0, lambda: self._openFile(self.settings.last_puzzle_path))

    def closeEvent(self, event):
        self.settings.save_settings()

    def update_recent_files(self, filePath=''):
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
        menu = self.recent_files_menu
        menu.clear()
        for file in recentFiles:
            menu.addAction(
                get_icon('blue-folder-open-document-text.png'),
                file, lambda file=file: self._openFile(file))
        if menu.isEmpty():
            noItemsAction = menu.addAction('Пусто')
            noItemsAction.setEnabled(False)

    def handle_puzzle_clear(self):
        self.board_view.model().board.clear()

    def handlePuzzleSolve(self):
        board = self.board_view.model().board
        for rowNo in range(board.row_count):
            self.statusBar().showMessage('Решается строка ' + str(rowNo))
            board.solve_row(rowNo)
        for columnNo in range(board.col_count):
            self.statusBar().showMessage('Решается колонка ' + str(columnNo))
            board.solveColumn(columnNo)
        self.statusBar().clearMessage()

    def handleFileOpen(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Открыть файл', self.settings.lastUsedDirectory,
            '*.nonogram (*.nonogram);;*.nonogram1 (*.nonogram1)')
        if filePath:
            self.settings.lastUsedDirectory = os.path.dirname(filePath)
            self._openFile(filePath)

    def _openFile(self, filePath):
        if filePath.endswith('.nonogram1'):
            self.board_view.model().board.load1(filePath)
        elif filePath.endswith('.nonogram'):
            self.board_view.model().board.load(filePath)
        else:
            return
        puzzle_name = os.path.splitext(os.path.basename(filePath))[0]
        self.setWindowTitle('%s - Японские кроссворды' % puzzle_name)
        self.settings.last_puzzle_path = filePath
        # add to recent files
        self.update_recent_files(filePath)

    def fileSave(self):
        self.board_view.model().board.save()

    def show_help_about(self):
        help.showAboutInfo(self)

    def show_help_usage(self):
        help.showUsageInfo(self)

    def createAction(self, text, slot=None, shortcut=None, icon='', tip=None,
                     checkable=False, signal='triggered'):
        """Convenience function to create PyQt actions.
        """
        action = QtWidgets.QAction(text, self)
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


from . import settings, help, board
