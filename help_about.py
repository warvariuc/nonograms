import platform

from PyQt4 import QtGui, QtCore


def showAboutInfo(mainWindow):
    QtGui.QMessageBox.about(mainWindow, 'О игре "Японские кроссворды"', """
<p><b><a href="http://ru.wikipedia.org/wiki/Японский_кроссворд">Японская
головоломка</a></b> (также <b>японский кроссворд</b>, <b>японское
рисование</b>, <b>нонограмма</b>) — головоломка, в которой, в отличие от
обычных кроссвордов, зашифрованы не слова, а изображения.</p>

<p>Изображения зашифрованы числами, расположенными слева от строк, а также
сверху над столбцами. Числа показывают, сколько групп чёрных клеток находятся в
соответствующих строке или столбце и сколько слитных клеток содержит каждая из
этих групп. Например, набор чисел 4, 1, и 3 означает, что в этом ряду есть три
группы: первая — из четырёх, вторая — из одной, третья — из трёх чёрных клеток.
Группы должны быть разделены, как минимум, одной пустой клеткой. Необходимо
определить размещение групп клеток.</p>

<p>Автор <a href="mailto:victor.varvariuc@gmail.com">Виктор Варварюк</a>.</p>

<p>Это приложение использует <a href="http://p.yusukekamiyamane.com/">Fugue
Icons</a>.</p>

<p>Информация о среде исполнения:<br>
Python {}, Qt {}, PyQt {}, OS {}</p>
""".format(platform.python_version(), QtCore.QT_VERSION_STR,
           QtCore.PYQT_VERSION_STR, platform.system()))
