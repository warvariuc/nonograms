from PyQt4 import QtCore, QtGui
import os, sys

appDir = QtGui.qApp.appDir

class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(appDir, 'icons', 'nonograms-logo.png')))
        
        self.boardView = __import__('board').BoardView()
        self.setCentralWidget(self.boardView)
        self.statusBar()
        
        #Create menu
        self.fileMenu = self.menuBar().addMenu('Файл')
        self.actionFileOpen = self.createAction('Открыть…', self.handleFileOpen, QtGui.QKeySequence.Open, 'folder-open-document-text.png')
        self.addActions(self.fileMenu, (self.actionFileOpen, ))
        self.recentFilesMenu = self.fileMenu.addMenu(QtGui.QIcon(os.path.join(appDir, 'icons', 'folders-stack.png')), 'Недавние файлы')
        self.recentFilesMenu.aboutToShow.connect(self.updateRecentFiles)
        self.actionFileSave = self.createAction('Сохранить', self.fileSave, QtGui.QKeySequence.Save, 'disk-black.png')
        self.addActions(self.fileMenu, (self.actionFileSave, self.createAction('Выход', self.close, 'Ctrl+Q', 'cross-button.png')))

        
        self.helpMenu = self.menuBar().addMenu('Помощь')
        self.addActions(self.helpMenu, (self.createAction('О программе', self.helpAbout, icon='question-button.png'), ))

        self.setWindowTitle('Японские кроссворды')
        
        self.fileToolbar = self.addToolBar('File')
        self.fileToolbar.setIconSize(QtCore.QSize(16,16))
        self.fileToolbar.addAction(self.actionFileOpen)
        self.fileToolbar.addAction(self.actionFileSave)

        self.puzzleToolbar = self.addToolBar('Puzzle')
        self.puzzleToolbar.setIconSize(QtCore.QSize(16,16))
        self.actionPuzzleClear = self.createAction('Очистить', self.handlePuzzleClear)
        self.puzzleToolbar.addAction(self.actionPuzzleClear)
        self.actionPuzzleSolve = self.createAction('Решить', self.handlePuzzleSolve, icon='nonograms-logo.png')
        self.puzzleToolbar.addAction(self.actionPuzzleSolve)
        
        
        import settings
        self.settings = settings.Settings(self)
        self.settings.readSettings()


    def closeEvent(self, event):
        #if w.requestExit() == False: #именно False, иначе None тоже считается отрицательным
            #event.ignore()
            #return
        self.settings.saveSettings()

    def updateRecentFiles(self, filePath=''):
        recentFiles = self.settings.recentFiles
        for i in range(len(recentFiles)-1, -1, -1): # remove from the list deleted files
            if not os.path.isfile(recentFiles[i]): del recentFiles[i]
            
        if filePath: #the funtion adds a file to recent files list if file name given otherwise updates the menu
            filePath = os.path.abspath(filePath)
            try: recentFiles.pop(recentFiles.index(filePath))
            except ValueError: pass
            recentFiles.insert(0, filePath)
            del recentFiles[10:] #keep 10 last files
            return
        menu = self.recentFilesMenu
        menu.clear()
        for file in recentFiles:
            menu.addAction(QtGui.QIcon(os.path.join(appDir, 'icons', 'blue-folder-open-document-text.png')), file, lambda file=file: self._openFile(file))
        if menu.isEmpty():
            noItemsAction = menu.addAction('Пусто')
            noItemsAction.setEnabled(False)

    def handlePuzzleClear(self):
        self.boardView.model().board.clear()
                
    def handlePuzzleSolve(self):
        board = self.boardView.model().board
        for rowNo in range(board.rows):
            self.statusBar().showMessage('Решается строка ' + str(rowNo))
            board.solveRow(rowNo)
        for columnNo in range(board.columns):
            self.statusBar().showMessage('Решается колонка ' + str(columnNo))
            board.solveColumn(columnNo)
        self.statusBar().clearMessage()

    def handleFileOpen(self):
        filePath = QtGui.QFileDialog.getOpenFileName(self,
                'Открыть файл', self.settings.lastUsedDirectory, '1 (*.nonogram1);;2 (*.nonogram2)')
        if filePath: 
            self.settings.lastUsedDirectory = os.path.dirname(filePath)
            self._openFile(filePath)

    def _openFile(self, filePath):
        if filePath.endswith('.nonogram1'):
            self.boardView.model().board.load1(filePath)
        self.updateRecentFiles(filePath) # add to recent files if the opening was successful

    def fileSave(self):
        self.boardView.model().board.save()
        #QtGui.QMessageBox.warning(self, 'Not implemented', 'This feature is not yet implemented')

    def helpAbout(self):
        __import__('help_about').showAboutInfo(self)
        
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal='triggered'):
        #Convenience function to create PyQt actions
        action = QtGui.QAction(text, self)
        if icon is not None: action.setIcon(QtGui.QIcon(os.path.join(appDir, 'icons', icon)))
        if shortcut is not None: action.setShortcut(shortcut)
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
            if action: menu.addAction(action)
            else: menu.addSeparator()
