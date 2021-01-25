from shibo_matPaint import Mygraphview
from _pycom import Qserial_threads
from shiboqi_main import Ui_MainWindow
import sys
from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtCore import QTimer
import queue
"""
    Qserial_threads: 
    Mygraphview: 
"""
class main_show(Qserial_threads,Mygraphview):
    def __init__(self,parent = None):
        global qx, qy, qz
        qx = queue.Queue(100000)
        qy = queue.Queue(100000)
        qz = queue.Queue(100000)

        super(main_show, self).__init__(parent, qx, qy, qz)

        self.paint_plot()

        # self.timerPlot = QTimer(self)
        # print("打印")
        # self.timerPlot.timeout.connect(self.paint_plot)
        # self.timerPlot.start(100)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_show1 = main_show()
    main_show1.show()
    sys.exit(app.exec_())
