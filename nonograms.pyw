#!/usr/bin/env python3

import sys

if sys.hexversion < 0x03010000:
    print("At least Python 3.1 needed. Exiting.");
    sys.exit(1) 


import os
from PyQt4 import QtCore, QtGui


app = QtGui.QApplication(sys.argv)
app.setOrganizationName('warvar')
app.setApplicationName('nonograms')


appDir = os.path.dirname(os.path.abspath(sys.argv[0]))
QtGui.qApp.appDir = appDir


mainWindow = __import__('main_window').MainWindow()
mainWindow.show()

def exception_hook(exc_type, exc_value, exc_traceback): # Global function to catch unhandled exceptions (mostly in user modules)
    import traceback
    info = ''.join (traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(info)
    QtGui.QMessageBox.warning(mainWindow, 'Exception', str(info))
    
sys.excepthook = exception_hook

res = app.exec() # start the event loop
sys.exit(res)