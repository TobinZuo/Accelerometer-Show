import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
matplotlib.use("Qt5Agg")  # 声明使用QT5
from shiboqi_main import Ui_MainWindow
from PyQt5 import QtCore, QtGui,QtWidgets
import queue
from PyQt5.QtCore import QTimer
import time
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
import random
import numpy as np
from scipy import interpolate
queueSize = 1000
axisLength = 2000

class Figure_Canvas(FigureCanvas):
        # 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplot                                          lib的关键
        def __init__(self, qx , qy , qz, parent=None, width=8, height=6, dpi=100):
            fig = Figure(figsize=(width, height),
                         dpi=dpi)  # 创建一个Figure，注意：该Figure为matplotlib下的figure，不是matplotlib.pyplot下面的figure
            #super(Figure_Canvas, self).__init__(self, fig)
            FigureCanvas.__init__(self, fig)  # 初始化父类
            #Ui_MainWindow.__init__(self)
            #QtWidgets.QMainWindow.__init__(self)

            self.setParent(parent) # 这里是调用的c++写的函数，所以看不到源码，https://doc.qt.io/archives/qt-4.8/qwidget.html#setParent
            self.ax1 = fig.add_subplot(311)  # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
            self.ax2 = fig.add_subplot(312)
            self.ax3 = fig.add_subplot(313)
            #self.ax1.axis("tight")
            self.ax1.set_xlim(0, axisLength)
            self.ax2.set_xlim(0, axisLength)
            self.ax3.set_xlim(0, axisLength)

            self.isFixedAxis = False
            self.xBoundary = 0.5
            self.yBoundary = 0.5
            self.zBoundary = 0.5
            self.ax1.set_title("X")
            self.ax2.set_title("Y")
            self.ax3.set_title("Z")
            fig.subplots_adjust(wspace= 0, hspace= 0.5)
            #
            # self.ax1.set_ylim(-2, 2)
            # self.ax2.set_ylim(-2, 2)
            # self.ax3.set_ylim(-2, 2)

            self.dataX = []
            self.dataY = []
            self.dataZ = []
            self.qx = qx
            self.qy = qy
            self.qz = qz
            self.xPos = 0
            self.yPos = 0
            self.zPos = 0

            self.curRightPos = 0
            self.ax1.plot()
            self.ax2.plot()
            self.ax3.plot()



        def test(self):
            # self.ax1.cla()
            # x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            # y = [23, 21, 32, 13, 3, 132, 13, 3, 1]
            # self.ax1.plot(x, y)
            # self.draw()

            x = np.linspace(0, 10, 10)
            y = [random.randint(0, 10) for i in range(10)]
            xx = np.linspace(0, 10)
            f = interpolate.interp1d(x, y, 'quadratic')  # 产生插值曲线的函数
            yy = f(xx)
            self.ax1.cla()
            self.ax1.plot(x, y, 'o', xx, yy)
            self.draw()
        def plotXYZ(self):
            length = self.qx.qsize()
            while length > 0:
                self.dataX.append(self.qx.get())
                self.dataY.append(self.qy.get())
                self.dataZ.append(self.qz.get())

                length -= 1
            dataXLen = len(self.dataX)

            if dataXLen < axisLength:
                try:
                    self.ax1.cla()
                    self.ax1.set_xlim(0, 1000)
                    self.ax1.set_title("X")
                    self.ax1.plot(range(0, dataXLen), self.dataX[0: dataXLen])


                    self.ax2.cla()
                    self.ax2.set_xlim(0, 1000)
                    self.ax2.set_title("Y")

                    #self.ax2.set_ylim(-1, 1)
                    self.ax2.plot(range(0, dataXLen), self.dataY[0: dataXLen])

                    self.ax3.cla()
                    self.ax3.set_xlim(0, 1000)
                    self.ax3.set_title("Z")

                    #self.ax3.set_ylim(-1, 1)
                    self.ax3.plot(range(0, dataXLen), self.dataZ[0: dataXLen])

                    if self.isFixedAxis:
                        self.ax1.set_ylim(-self.xBoundary, self.xBoundary)
                        self.ax2.set_ylim(-self.yBoundary, self.yBoundary)
                        self.ax3.set_ylim(-self.zBoundary, self.zBoundary)
                    self.draw()
                except Exception as e:
                    print(e)
            else:
                board = 0.1
                try:
                    self.ax1.cla()
                    # self.ax1.set_ylim(-board, board)
                    self.ax1.set_title("X")

                    self.ax1.plot(range(dataXLen-axisLength, dataXLen), self.dataX[dataXLen-axisLength: dataXLen])

                    self.ax2.cla()
                    self.ax2.set_title("Y")
                    # self.ax2.set_ylim(-board, board)
                    self.ax2.plot(range(dataXLen-axisLength, dataXLen), self.dataY[dataXLen-axisLength: dataXLen])

                    self.ax3.cla()
                    self.ax3.set_title("Z")
                    # self.ax3.set_ylim(-board, board)
                    self.ax3.plot(range(dataXLen-axisLength, dataXLen), self.dataZ[dataXLen-axisLength: dataXLen])

                    if self.isFixedAxis:
                        self.ax1.set_ylim(-self.xBoundary, self.xBoundary)
                        self.ax2.set_ylim(-self.yBoundary, self.yBoundary)
                        self.ax3.set_ylim(-self.zBoundary, self.zBoundary)

                    self.draw()
                except Exception as e:
                    print(e)
            # #print(length)
            # try:
            #     for i in range(length):
            #         time.sleep(0.01)
            #         if len(self.dataX) >= 50:
            #             print("打印图像中")
            #             self.ax1.cla()
            #             self.ax1.plot(range(0, 50), self.dataX)
            #             self.draw()
            #
            #             self.dataX[:-1] = self.dataX[1:]
            #             self.dataX.pop()
            #         self.dataX.append(self.q.get())
            # except Exception as e:
            #     print(e)
        def plot(self):
            try:
                self.timerPlot = QTimer(self)
                self.timerPlot.timeout.connect(self.plotXYZ)
                self.timerPlot.start(50)
            except Exception as e:
                print(e)

#创建一个GraphicsView实例化显示
class Mygraphview(Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self, parent = None, qx = queue.Queue(queueSize), qy = queue.Queue(queueSize), qz = queue.Queue(queueSize)):
        super(Mygraphview,self).__init__(parent)
        self.setupUi(self)
        self.qx = qx
        self.qy = qy
        self.qz = qz

        self.show()
        #self.paint_plot()



    #将波形嵌入QGraph_view控件
    def paint_plot(self):
        #print("画图：", self.q.qsize())
        self.Graphview = Figure_Canvas(qx=self.qx, qy=self.qy, qz=self.qz)
        try:
            # self.Graphview.plotx(self.q)
            self.Graphview.plot()
        except Exception as e:
            print(e)

        # 创建一个QGraphicsScene，因为加载的图形（FigureCanvas）
        # 不能直接放到graphicview控件中，必须先放到graphicScene
        # 然后再把graphicscene放到graphicview中
        graphicscene = QtWidgets.QGraphicsScene()
        # 把图形放到QGraphicsScene中
        # 注意：图形是作为一个QWidget放到QGraphicsScene中的
        graphicscene.addWidget(self.Graphview)
        self.graphicsView.setScene(graphicscene)  # 把QGraphicsScene放入QGraphicsView
        self.graphicsView.show()  # 调用show方法呈现图形！Voila!!
    # def paint_plotx(self):
    #     self.Graphview.plotx(self.q)


#
# class My_appwindow(SerialInit,Mygraphview):
#     #示波器上位机显示
#    def __init__(self):
#        super().__init__()
#        self.paint_plot()

