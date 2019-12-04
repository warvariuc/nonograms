import os
import glob
import random

from PyQt5 import QtGui, QtCore, QtWidgets


class Settings():

    def __init__(self, main_window):
        self.main_window = main_window

        self.path = QtCore.QStandardPaths.standardLocations(QtCore.QStandardPaths.DataLocation)[0]
        self.puzzle_dir = os.path.join(QtWidgets.qApp.appDir, 'puzzles')
        self.settings = QtCore.QSettings(
            self.path, QtCore.QSettings.IniFormat, self.main_window)
        self.read_settings()

    def read_settings(self):
        geometry = self.settings.value('geometry', None)
        if geometry:
            self.main_window.restoreGeometry(geometry)
        windowState = self.settings.value('windowState', None)
        if windowState:
            self.main_window.restoreState(windowState)
        else:
            # default main window size
            self.main_window.resize(640, 480)

        self.recentFiles = self.settings.value('recentFiles', None) or []
        self.lastUsedDirectory = self.settings.value(
            'lastUsedDirectory', self.puzzle_dir)
        self.last_puzzle_path = self.settings.value('lastPuzzlePath', None) or ''
        if not self.last_puzzle_path or not os.path.isfile(self.last_puzzle_path):
            # select a random puzzle
            puzzle_paths = glob.glob(
                os.path.join(self.puzzle_dir, '*.nonogram'))
            if puzzle_paths:
                self.last_puzzle_path = random.choice(puzzle_paths)

    def save_settings(self):
        self.settings.setValue('geometry', self.main_window.saveGeometry())
        self.settings.setValue('windowState', self.main_window.saveState())
        self.settings.setValue('recentFiles', self.recentFiles)
        self.settings.setValue('lastUsedDirectory', self.lastUsedDirectory)
        self.settings.setValue('lastPuzzlePath', self.last_puzzle_path)
