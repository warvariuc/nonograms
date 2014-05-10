__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import sys

if sys.hexversion < 0x03010000:
    print("At least Python 3.1 needed. Exiting.")
    sys.exit(1) 


import os

from PyQt4 import QtCore, QtGui


QtCore.pyqtRemoveInputHook()
app = QtGui.QApplication(sys.argv)
app.setOrganizationName('warvariuc')
app.setApplicationName('nonograms')


appDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
QtGui.qApp.appDir = appDir


from . import main_window


mainWindow = main_window.MainWindow()
mainWindow.show()

QtGui.qApp.mainWindow = mainWindow


def exception_hook(exc_type, exc_value, exc_traceback):
    """Global function to catch unhandled exceptions.
    """
    import traceback
    info = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(info)
    QtGui.QMessageBox.warning(mainWindow, 'Exception', str(info))


sys.excepthook = exception_hook
