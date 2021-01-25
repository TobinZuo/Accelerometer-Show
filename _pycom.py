import serial
import serial.tools.list_ports
from shiboqi_main import Ui_MainWindow
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
import time
import binascii
import queue
import pandas as pd
import numpy as np
# 设立串口初始化
ququeSize = 100000
import time
class SerialInit(Ui_MainWindow,QtWidgets.QMainWindow):

    def __init__(self, parent = None, qx = queue.Queue(ququeSize), qy = queue.Queue(ququeSize), qz = queue.Queue(ququeSize)):
        self.qx = qx
        self.qy = qy
        self.qz = qz

        self.allDataXaxisDecimal = []
        self.allDataYaxisDecimal = []
        self.allDataZaxisDecimal = []
        super(SerialInit, self).__init__(parent)
        self.setupUi(self)
        #self.paint_plot()

        # 是否是第一条数据，第一条数据需要校准位置
        self.isFirst = True

        # 串口失效
        self.ser = None
        # 串口数据接受量和记录数据量
        self.receive_num = 0
        self.record_num = 0
        # 串口接收的所有字节
        self.allDataHex = b''

        # 是否开始记录标志
        self.isRecord = False
        # 打印的位置
        self.printPos = 0
        # 显示接收的字符数量
        dis = ' 接收:' + '{:d}'.format(self.receive_num)

        self.statusbar.showMessage(dis)
        # 显示记录的数据量和时间长度
        record = ' 记录:' + '{:d}'.format(self.record_num)
        self.recordTimeLength = 0

        # 减均值的窗口大小
        self.averageWindowSize = 100
        self.isMinusAverageData = False
        self.lineEdit_3.setText("100")
        # 刷新一下串口的列表
        self.refresh()

        # 波特率
        self.comboBox_2.addItem('256000')
        self.comboBox_2.addItem('115200')
        self.comboBox_2.addItem('57600')
        self.comboBox_2.addItem('56000')
        self.comboBox_2.addItem('38400')
        self.comboBox_2.addItem('19200')
        self.comboBox_2.addItem('14400')
        self.comboBox_2.addItem('9600')
        self.comboBox_2.addItem('4800')
        self.comboBox_2.addItem('2400')
        self.comboBox_2.addItem('1200')

        # 数据位
        self.comboBox_3.addItem('8')
        self.comboBox_3.addItem('7')
        self.comboBox_3.addItem('6')
        self.comboBox_3.addItem('5')

        # 停止位
        self.comboBox_4.addItem('1')
        self.comboBox_4.addItem('1.5')
        self.comboBox_4.addItem('2')

        # 校验位
        self.comboBox_5.addItem('NONE')
        self.comboBox_5.addItem('ODD')
        self.comboBox_5.addItem('EVEN')

        #测试数据访问
        # self.comboBox_6.addItem('正弦波')
        # self.comboBox_6.addItem('方波')

        # 对testEdit进行事件过滤
        #self.textEdit.installEventFilter(self)

        # 实例化一个接受数据定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.recv)
        #self.timer.start(10)

        # 减均值
        self.pushButton_8.clicked.connect(self.minusAvergeData)
        # 开始记录数据
        self.pushButton_6.clicked.connect(self.recordData)
        # 选择文件夹保存数据
        self.pushButton_7.clicked.connect(self.saveData)

        # 刷新串口外设按钮
        self.pushButton_2.clicked.connect(self.refresh)
        # 打开关闭串口按钮
        self.pushButton.clicked.connect(self.open_close)
        self.isClosed = True
        # 波特率修改
        self.comboBox_2.activated.connect(self.baud_modify)
        # 串口号修改
        self.comboBox.activated.connect(self.com_modify)
        # 执行一下打开串口

        #self.open_close(True)
        #self.pushButton.setChecked(True)

        # 刷新一下串口

    def refresh(self):
        # 查询可用的串口
        plist = list(serial.tools.list_ports.comports())

        if len(plist) <= 0:
            print("No used com!");
            self.statusbar.showMessage('没有可用的串口')


        else:
            # 把所有的可用的串口输出到comboBox中去
            self.comboBox.clear()

            for i in range(0, len(plist)):
                plist_0 = list(plist[i])
                self.comboBox.addItem(str(plist_0[0]))

    # 重载窗口关闭事件
    def closeEvent(self, e):
    #关闭定时器，停止读取接收数据
        #self.timer_send.stop()
        self.timer.stop()

        #关闭串口
        if self.ser != None:
            self.ser.close()

    # 事件过滤
    def eventFilter(self, obj, event):
        # 处理textEdit的键盘按下事件
        if event.type() == event.KeyPress:

            if self.ser != None:
                char = event.text()
                num = self.ser.write(char.encode('utf-8'))
                self.send_num = self.send_num + num
                #dis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
                #self.statusBar.showMessage(dis)
            '''else:
                pass
            return True

            return False'''

    # 波特率修改
    def baud_modify(self):
        if self.ser != None:
            self.ser.baudrate = int(self.comboBox_2.currentText())

    # 串口号修改
    def com_modify(self):
        if self.ser != None:
            self.ser.port = self.comboBox.currentText()

    def recordData(self):
        if self.isRecord == False:
            self.timeRecordStart = time.time()
            # 获取开始的时间戳

            self.allRecordDataXaxisDecimal = []
            self.allRecordDataYaxisDecimal = []
            self.allRecordDataZaxisDecimal = []
            self.pushButton_6.setText("停止记录")
            self.isRecord = True
            print('开始记录')
            self.record_num = 0

        else:
            self.timeRecordEnd = time.time()
            # 获取停止的时间戳

            self.recordTimeLength = self.timeRecordEnd - self.timeRecordStart
            self.pushButton_6.setText("开始记录")
            self.isRecord = False
            print('停止记录')

    def saveData(self):
        # 输入保存的文件名称
        text, ok = QInputDialog.getText(self, "保存的文件名", "请输入文件名：(比如：jump_0.5m_A)", text = self.lineEdit_4.text())
        # 选择保存的文件路径
        # getDirectoryPath = QFileDialog.getExistingDirectory(self, "选取指定文件夹", "E:\Jupyter\实验室\采集数据")
        try:
            allRecordDataXYZList = [self.allRecordDataXaxisDecimal, self.allRecordDataYaxisDecimal, self.allRecordDataZaxisDecimal]
            allRecordDataXYZDataFrame = pd.DataFrame(columns=['x', 'y', 'z'], data = np.asarray(allRecordDataXYZList).T)
            timeStartEnd = pd.DataFrame(columns=['start_time', 'end_time'], data=np.asarray([[self.timeRecordStart, self.timeRecordEnd]]))
            getDirectoryPath = r"E:\Jupyter\实验室\采集数据"
            print(str(getDirectoryPath) + "\\" + text + '.csv')
            allRecordDataXYZDataFrame.to_csv(str(getDirectoryPath)+"\\" + text + '.csv', encoding="utf-8", index = False)
            timeStartEnd.to_csv(str(getDirectoryPath)+"\\" + text + '_time.csv', encoding="utf-8", index = False)

        except Exception as e:
            print(e)
    # 打开关闭串口
    def open_close(self):
        btn_sta = self.isClosed
        if btn_sta == True:
            try:
                # 输入参数'COM13',115200
                print(self.comboBox.currentText())
                self.ser = serial.Serial(self.comboBox.currentText(), int(self.comboBox_2.currentText()), timeout=0.2)
                self.ser.flushInput()
                self.isClosed = False
            except:
                QMessageBox.critical(self, '串口提示', '没有可用的串口或当前串口被占用')
                return None
            # 字符间隔超时时间设置
            self.ser.interCharTimeout = 0.001
            # 1ms的测试周期
            self.timer.start(2)
            self.pushButton.setText("关闭串口")
            print('open')
        else:
            print("关闭串口中")
            # 关闭定时器，停止读取接收数据
            #self.timer_send.stop()
            self.timer.stop()

            try:
                # 关闭串口
                self.ser.close()
                self.isClosed = True
            except:
                QMessageBox.critical(self, '串口提示', '关闭串口失败')
                return None

            self.ser = None

            self.pushButton.setText("打开串口")
            print('close!')
            # 串口接收数据处理
    def minusAvergeData(self):
        try:
            if self.lineEdit_3.text() == '':
                self.averageWindowSize = 0
                print("未输入数据")
            else:
                if self.isMinusAverageData == False:
                    self.isMinusAverageData = True
                    self.averageWindowSize = int(self.lineEdit_3.text())
                    self.pushButton_8.setText("取消减均值")
                    print(self.averageWindowSize)
                else:
                    self.averageWindowSize = 0
                    self.isMinusAverageData = False
                    self.pushButton_8.setText("减均值")
        except Exception as e:
            print(e)

    def recv(self):
        try:
            num = self.ser.inWaiting()
        except Exception as e:
            print("recv is down ", e)
            self.timer_send.stop()
            self.timer.stop()
            # 串口拔出错误，关闭定时器
            self.ser.close()
            self.ser = None

            # 设置为打开按钮状态
            self.pushButton.setChecked(False)
            self.pushButton.setText("打开串口")
            print('serial error!')
            return None
        if self.isFirst and num >= 18 or num > 0:
            data = self.ser.read(num)
            data_hex = binascii.b2a_hex(data) # 二进制转为十六进制的字符流
            # print(len(data))
            if self.isFirst:
                self.isFirst = False
                while True:
                    print(data_hex[5], data_hex[11], data_hex[17])
                    # 直接访问十六进制的字符流得到的是对应字符的ASCII值
                    # 比如a = b'hello'的十六进制字符流->a = "68656c6c6f"直接访问a[9] = 102，返回的是f的ascii值
                    # ord就是将字符转为ascii值，传感器有4bit用来标记
                    if data_hex[5] == ord('1') and data_hex[11] == ord('0') and data_hex[17] == ord('0'):
                        print("Fine")
                        break
                    else:
                        print("Remove first 1 bytes")
                        data_hex = data_hex[2:]

            # print(type(data)) bytes

            # 调试打印输出数据
            #print(data)
            self.allDataHex += data_hex
            #print(data_hex)
            #print("所有数据长度：", len(self.allDataHex) // 18)
            x = []
            y = []
            z = []
            start = time.time()
            for i in range(self.printPos, len(self.allDataHex) // 18):
                ix = i * 18
                # print(self.allDataHex[ix:ix + 6], self.allDataHex[ix + 6:ix + 12], self.allDataHex[ix + 12:ix + 18])
                x.append((int(self.allDataHex[ix:ix + 5], 16) - 2 ** 20) / 2 ** 18 if int(self.allDataHex[ix:ix + 5], 16) > 2 ** 19 \
                             else (int(self.allDataHex[ix:ix + 5], 16) / 2 ** 18))
                y.append((int(self.allDataHex[ix + 6:ix + 11], 16) - 2 ** 20) / 2 ** 18 if int(self.allDataHex[ix + 6:ix + 11],
                                                                                        16) > 2 ** 19 \
                             else (int(self.allDataHex[ix + 6:ix + 11], 16) / 2 ** 18))
                z.append((int(self.allDataHex[ix + 12:ix + 17], 16) - 2 ** 20) / 2 ** 18 if int(self.allDataHex[ix + 12:ix + 17],
                                                                                         16) > 2 ** 19 \
                             else (int(self.allDataHex[ix + 12:ix + 17], 16) / 2 ** 18))

            #self.printPos += len(data_hex) // 18
            if self.isRecord == True:
                self.allRecordDataXaxisDecimal.extend(x)
                self.allRecordDataYaxisDecimal.extend(y)
                self.allRecordDataZaxisDecimal.extend(z)
            if len(x) > 0:
                self.allDataXaxisDecimal.extend(x)
                self.allDataYaxisDecimal.extend(y)
                self.allDataZaxisDecimal.extend(z)
            end = time.time()
            # if end - start > 0:
            #     print(end - start)

            length = len(x)
            try:
                if self.isMinusAverageData and len(self.allDataXaxisDecimal) > self.averageWindowSize:
                    if self.printPos + len(x) - length - self.averageWindowSize >= 0:
                        while length > 0:
                            if self.qx.full():
                                self.qx.get()
                            if self.qy.full():
                                self.qy.get()
                            if self.qz.full():
                                self.qz.get()

                            self.qx.put(x[len(x) - length]-np.asarray(self.allDataXaxisDecimal[self.printPos+len(x)-length-self.averageWindowSize: self.printPos+len(x)-length]).mean())
                            self.qy.put(y[len(y) - length]-np.asarray(self.allDataYaxisDecimal[self.printPos+len(x)-length-self.averageWindowSize: self.printPos+len(x)-length]).mean())
                            self.qz.put(z[len(z) - length]-np.asarray(self.allDataZaxisDecimal[self.printPos+len(x)-length-self.averageWindowSize: self.printPos+len(x)-length]).mean())
                            length -= 1
                else:
                    while length > 0:
                        if self.qx.full():
                            self.qx.get()
                        if self.qy.full():
                            self.qy.get()
                        if self.qz.full():
                            self.qz.get()
                        self.qx.put(x[len(x)-length])
                        self.qy.put(y[len(y)-length])
                        self.qz.put(z[len(z)-length])
                        length -= 1
            except Exception as e:
                # pass
                print(e)
            # 放在压入队列之后更改
            self.printPos = len(self.allDataHex) // 18
            # 统计接收字符的数量
            # 统计接收字符的数量, 统计保存的数据点个数和时间长度
            if self.isRecord == True:
                self.receive_num = self.receive_num + len(x)
                dis = '接收: ' + '{:d}'.format(self.receive_num)
                self.record_num = self.record_num + len(x)
                record = '当前记录->  ' + '数据点个数: {:d}'.format(self.record_num) + "    " + '时间长度：{:.2f}'.format(time.time() - self.timeRecordStart) + "秒"
                self.statusbar.showMessage(dis + "       " + record)
            else:
                self.receive_num = self.receive_num + len(x)
                record = '上次记录->  ' + '数据点个数: {:d}'.format(self.record_num) + "    " + '时间长度：{:.2f}'.format(
                        self.recordTimeLength) + "秒"

                dis = '接收: ' + '{:d}'.format(self.receive_num)
                self.statusbar.showMessage(dis + "       " + record)

        #     # 十六进制显示
        #     if self.checkBox_3.checkState():
        #         out_s = ''
        #         for i in range(0, len(data)):
        #             out_s = out_s + '{:02X}'.format(data[i]) + ' '
        #
        #     else:
        #         # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
        #         out_s = data.decode('iso-8859-1')
        #
        #         if self.rcv_enter == '\r':
        #             # 上次有回车未显示，与本次一起显示
        #             out_s = '\r' + out_s
        #             self.rcv_enter = ''
        #
        #         if out_s[-1] == '\r':
        #             # 如果末尾有回车，留下与下次可能出现的换行一起显示，解决textEdit控件分开2次输入回车与换行出现2次换行的问题
        #             out_s = out_s[0:-1]
        #             self.rcv_enter = '\r'
        #
        #     # 先把光标移到到最后
        #     cursor = self.textEdit.textCursor()
        #     if (cursor != cursor.End):
        #         cursor.movePosition(cursor.End)
        #         self.textEdit.setTextCursor(cursor)
        #
        #     # 把字符串显示到窗口中去
        #     self.textEdit.insertPlainText(out_s)
        #
        #     # 统计接收字符的数量
        #     self.receive_num = self.receive_num + num
        #     dis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
        #     self.statusbar.showMessage(dis)
        #
        #     # 获取到text光标
        #     textCursor = self.textEdit.textCursor()
        #     # 滚动到底部
        #     textCursor.movePosition(textCursor.End)
        #     # 设置光标到text中去
        #     self.textEdit.setTextCursor(textCursor)
        # else:
        #     # 此时回车后面没有收到换行，就把回车发出去
        #     if self.rcv_enter == '\r':
        #         # 先把光标移到到最后
        #         cursor = self.textEdit.textCursor()
        #         if (cursor != cursor.End):
        #             cursor.movePosition(cursor.End)
        #             self.textEdit.setTextCursor(cursor)
        #         self.textEdit.insertPlainText('\r')
        #         self.rcv_enter = ''



#设立串口进程
# QThread: 平台无关的管理线程的办法，一个QThread对象管理一个线程。QThread的执行从run函数执行开始，在Qt自带的QThread雷中，run
# 函数通过调用exec()函数来启动时间循环机制，并且在线程内部处理Qt的事件，在Qt中建立线程的主要目的就是为了用线程来处理耗时的后台
# 操作，从而能让主界面及时响应用户的请求操作
class Qserial_threads(SerialInit,QtCore.QThread):

    # 声明一个信号，同时返回一个list，同理什么都能返回啦
    # signal用于线程之间的通信,即触发了某个控件时，另一个控件的状态也要跟着变化。通过signal和slot来实现通信
    # finishSignal.connect(某个slot函数)
    # finishSignal.emit(某个list) 就会执行响应的slot函数
    finishSignal = QtCore.pyqtSignal(list)

    # 构造函数里增加形参
    # parent: None, 若不为空，则说明当前小部件成为父级的子窗口。删除parent父级窗口，将会删除新窗口小部件
    def __init__(self, parent=None, qx = queue.Queue(ququeSize), qy = queue.Queue(ququeSize), qz = queue.Queue(ququeSize)):
        super(Qserial_threads, self).__init__(parent, qx, qy, qz)
        # 储存参数


    def run(self):
        pass




