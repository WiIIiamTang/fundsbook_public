from PyQt5.QtCore import pyqtSignal, QObject

class ThreadWorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(str)
    progress_num = pyqtSignal(int)