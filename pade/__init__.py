try:
    from PySide import QtGui
    import sys
    app = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
except:
    from twisted.internet import reactor
