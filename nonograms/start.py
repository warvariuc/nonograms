import sys

if sys.hexversion < 0x03010000:
    print("At least Python 3.1 needed. Exiting.")
    sys.exit(1) 


import os

from PyQt5 import QtCore, QtGui, QtWidgets


QtCore.pyqtRemoveInputHook()
app = QtWidgets.QApplication(sys.argv)
app.setOrganizationName('warvariuc')
app.setApplicationName('nonograms')


appDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
QtWidgets.qApp.appDir = appDir


from . import main_window


mainWindow = main_window.MainWindow()
mainWindow.show()

QtWidgets.qApp.mainWindow = mainWindow


def exception_hook(exc_type, exc_value, exc_traceback):
    """Global function to catch unhandled exceptions.
    """
    import traceback
    info = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(info)
    QtWidgets.QMessageBox.warning(mainWindow, 'Exception', str(info))


sys.excepthook = exception_hook
