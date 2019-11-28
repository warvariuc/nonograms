import os
import glob
import random

from PyQt5 import QtGui, QtCore, QtWidgets


class Settings():

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

        self.path = QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.DataLocation)[0]
        self.puzzle_dir = os.path.join(QtWidgets.qApp.appDir, 'puzzles')
        self.settings = QtCore.QSettings(
            self.path, QtCore.QSettings.IniFormat, self.mainWindow)
        self.readSettings()

    def readSettings(self):
        geometry = self.settings.value('geometry', None)
        if geometry:
            self.mainWindow.restoreGeometry(geometry)
        windowState = self.settings.value('windowState', None)
        if windowState:
            self.mainWindow.restoreState(windowState)
        else:
            # default main window size
            self.mainWindow.resize(640, 480)

        self.recentFiles = self.settings.value('recentFiles', None) or []
        self.lastUsedDirectory = self.settings.value(
            'lastUsedDirectory', self.puzzle_dir)
        self.lastPuzzlePath = self.settings.value('lastPuzzlePath', None) or ''
        if not self.lastPuzzlePath or not os.path.isfile(self.lastPuzzlePath):
            # select a random puzzle
            puzzle_paths = glob.glob(
                os.path.join(self.puzzle_dir, '*.nonogram'))
            if puzzle_paths:
                self.lastPuzzlePath = random.choice(puzzle_paths)

    def saveSettings(self):
        self.settings.setValue('geometry', self.mainWindow.saveGeometry())
        self.settings.setValue('windowState', self.mainWindow.saveState())
        self.settings.setValue('recentFiles', self.recentFiles)
        self.settings.setValue('lastUsedDirectory', self.lastUsedDirectory)
        self.settings.setValue('lastPuzzlePath', self.lastPuzzlePath)
