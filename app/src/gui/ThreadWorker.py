from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, pyqtSlot, QObject
from .Signals import ThreadWorkerSignals
import traceback, sys

class ThreadWorker(QRunnable):
    '''
    Represents a worker that handles thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, fn, *args, **kwargs):
        super(ThreadWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadWorkerSignals()

        # Add the callback to our kwargs
        # These should be referenced in the function signature of the callback
        # eg. def foo(*args, progress_callback, progress_callback_num)
        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['progress_callback_num'] = self.signals.progress_num


    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done