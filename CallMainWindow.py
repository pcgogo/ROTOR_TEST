# 逻辑文件

from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from MainWindow import *
import serial
import serial.tools.list_ports
import sys
import time
import sip

import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from Data_Process import *



class MainWindow(QtWidgets.QMainWindow, Ui_Form):
    plotfinish=pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # 设置标题


        # 窗口位置移动到左上角
        self.move(0,0)

        # 寻找可用串口
        self.refresh()

        # 添加波特率
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
        self.comboBox_2.setCurrentIndex(6)

        # 声明串口相关标志位
        self.Ser = None
        self.send_num = 0
        self.receive_num = 0

        # 打开串口
        #self.mSerial = SerialPort('COM1', 9600)
        #self.mSerial.start()
        #self.Ser = True
        #print('serial open finish')
        self.Status.setText('请连接串口')

        # 初始化检测计数器
        self.count = 0 #检测计数
        self.counter.setText('已检测:'+str(self.count))

        # 模式选择（检测模式或标定模式）默认为检测模式
        self.RunMode = 'test'  # 'test'为检测模式 'calibration'为标定模式

        # 标定参数
        self.calibration_quantity = 1 # 参与标定的转子个数
        self.calibration_times = 1  # 每个转子测量次数

        #  标定数据
        self.calibration_data = []

        # 将GroupBox作为绘图区
        self.gridlayout = QGridLayout(self.groupBox)  # 继承容器groupBox

        # 读取配置信息
        try:
            self.readSettings()
        except:
            pass

        # disable结果显示textEidt
        self.ResultEdit.setEnabled(False)

        # 默认打开自动检测
        self.OpenAutoJudge.setChecked(True)

        # 信号和槽
        #self.mSerial.DataReceiveFinish.connect(self.plotdata)
        self.plotfinish.connect(self.afterplot)
        #self.mSerial.ReceivingData.connect(self.Receiving)
        #self.mSerial.ReceiveCounter.connect(self.ReceiveCounter)
        self.OpenAutoJudge.stateChanged.connect(self.writeSettings)
        self.SerOpenBtn.clicked.connect(self.open_close)
        self.CalibrationBtn.clicked.connect(self.calibration)

    def refresh(self):
         # 查询可用的串口
        plist = list(serial.tools.list_ports.comports())

        if len(plist) <= 0:
            QMessageBox.warning(self,'串口错误','没有可用的串口',QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        else:
            # 把所有的可用的串口输出到comboBox中去
            self.comboBox.clear()
            for i in range(0, len(plist)):
                plist_0 = list(plist[i])
                self.comboBox.addItem(str(plist_0[0]))

    def open_close(self):  # SerOpenBtn按钮clicked的槽函数，用来打开串口
        try:
            if self.Ser is None:
                self.mSerial = SerialPort(self.comboBox.currentText(), int(self.comboBox_2.currentText()))
                self.mSerial.start()
                self.Ser = True
                print('serial open finish')
                self.Status.setText('串口已连接:' + self.comboBox.currentText())
                self.SerOpenBtn.setText("串口已打开")
                self.SerOpenBtn.setEnabled(False)  # 以下三行代码：串口打开后不允许更改串口配置
                self.comboBox.setEnabled(False)  #
                self.comboBox_2.setEnabled(False)  #
                self.mSerial.DataReceiveFinish.connect(self.plotdata)
                self.mSerial.ReceivingData.connect(self.Receiving)
                self.mSerial.ReceiveCounter.connect(self.ReceiveCounter)
                self.mSerial.calibration_finish.connect(self.calibration_finish)  # 标定完成消息连接到槽函数
            else:
                try:
                    self.mSerial.stop()
                    self.mSerial.port_close()
                    self.SerOpenBtn.setText("打开串口")
                    self.Ser = None
                except:
                    QMessageBox.warning(self,'串口错误','请重启本程序',QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        except:
            QMessageBox.warning(self,'error','OpenSerialFalse')

    def Receiving(self):
        self.Status.setText('接收数据中')
        if self.count == 0:
            pass
        else:
            self.clearplot()

    def ReceiveCounter(self,receivecounter):
        self.Status.setText('接收数据中 ' + str(receivecounter) + '//3000')

    def clearplot(self): # 该函数用于清除绘图区，以便于下次测试绘图
        self.gridlayout.removeWidget(self.F) # 从继承的groupBox中将自定义控件删除
        sip.delete(self.F)  #删除对象F
        print('removeWidget')

    def afterplot(self):       # plotfinish的槽函数，在测试结束后计算峰峰值和周期，并向下位机发送信号
        if self.Ser is not None:
            #input_s = 'finish'
            #input_s = input_s.encode('utf-8')
            #num = self.mSerial.port.write(input_s)
            self.mSerial.data = []  # 清空串口接收列表
            self.mSerial.start() #串口接收线程重新启动
            time.sleep(2) # 主进程睡眠2s，避免操作太快使串口数据收发混乱
            self.Status.setText('检测完成')

        else:
            QMessageBox.warning(self, '串口错误', '串口未打开', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def plotdata(self, data):  # 数据绘图与显示函数
        self.F = MyFigure(width=3, height=2, dpi=100)  # 创建一个Figure作为绘图区,此时对象F相当于一个自定义的控件，具体请看MyFigure类的代码
        t = np.arange(0.0, 6.0, 0.006)  # 创建一个长度与数据个数相同的array，这里是1000
        s = filter(data[0:2998:3]) # 对1号传感器的数据进行滤波
        s = np.asarray(s)  # 将接受到的数据list存为array便于计算和绘图
        self.F.axes.plot(t, s)  # 在Figure的子图中绘制
        s2 = filter(data[1:2999:3])  # 同上，处理2号传感器数据
        s2 = np.asarray(s2)
        self.F.axes2.plot(t, s2)
        s3 = filter(data[2:3000:3])  # 同上，处理3号传感器的数据
        s3 = np.asarray(s3)
        self.F.axes3.plot(t, s3)
        self.F.fig.suptitle('rotor magnetic field')  # 给Figure起一个标题
        #self.gridlayout = QGridLayout(self.groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.F) # 在继承的groupBox中layout Figure
        print('plotdata finish') # 打印用于测试
        self.count+=1  # 检测计数＋1
        self.counter.setText('已检测:'+str(self.count))

        pp1 = find_pp(s)  # 用来保存每个峰峰值
        pp2 = find_pp(s2)
        pp3 = find_pp(s3)

        self.pp_value_max.setText('最大峰峰值: %.2f\t%.2f \t %.2f' % (max(pp1),max(pp2),max(pp3)))
        self.pp_value_min.setText('最小峰峰值: %.2f\t%.2f \t %.2f' % (min(pp1),min(pp2),min(pp3)))
        self.period.setText('平均周期:  %.2fs\t%.2fs\t%.2fs' % (find_period(s),find_period(s2),find_period(s3)))
        if self.OpenAutoJudge.isChecked():
            self.judge(s,s2,s3)
        self.plotfinish.emit() #发送绘图完成消息

    def judge(self,s1,s2,s3):  # 判断是否合格
        pp1 = find_pp(s1)
        pp2 = find_pp(s2)
        pp3 = find_pp(s3)
        t1 = find_period(s1)
        t2 = find_period(s2)
        t3 = find_period(s3)
        # 将textEdit中的输入保存到内存中
        maxp1 = float(self.Set_pp1_max.toPlainText())
        minp1 = float(self.Set_pp1_min.toPlainText())
        maxp2 = float(self.Set_pp2_max.toPlainText())
        minp2 = float(self.Set_pp2_min.toPlainText())
        maxp3 = float(self.Set_pp3_max.toPlainText())
        minp3 = float(self.Set_pp3_min.toPlainText())
        maxt1 = float(self.Set_T1_max.toPlainText())
        mint1 = float(self.Set_T1_min.toPlainText())
        maxt2 = float(self.Set_T2_max.toPlainText())
        mint2 = float(self.Set_T2_min.toPlainText())
        maxt3 = float(self.Set_T3_max.toPlainText())
        mint3 = float(self.Set_T3_min.toPlainText())
        # 判断逻辑
        if max(pp1) <= maxp1 and min(pp1 )>= minp1 and mint1 <= t1 <= maxt1:
            S1isOK = True
        else:
            S1isOK = False
        if max(pp2) <= maxp2 and min(pp2) >= minp2 and mint2 <= t2 <= maxt2:
            S2isOK = True
        else:
            S2isOK = False
        if max(pp3) <= maxp3 and min(pp3) >= minp3 and mint3 <= t3 <= maxt3:
            S3isOK = True
        else:
            S3isOK = False
        if S1isOK and S2isOK and S3isOK:  # 结果显示
            self.ResultEdit.setHtml("<font color='green' size='12'><green>正常</font>")
        else:
            self.ResultEdit.setHtml("<font color='red' size='12'><red>异常</font>")


    def writeSettings(self):  # 保存用户设置
        try:
            # 创建QSettings对象
            settings = QSettings('MySoft', 'QtPad')
            # 保存用户设置
            settings.setValue('maxp1', QVariant(self.Set_pp1_max.toPlainText()))
            settings.setValue('minp1', QVariant(self.Set_pp1_min.toPlainText()))
            settings.setValue('maxp2', QVariant(self.Set_pp2_max.toPlainText()))
            settings.setValue('minp2', QVariant(self.Set_pp2_min.toPlainText()))
            settings.setValue('maxp3', QVariant(self.Set_pp3_max.toPlainText()))
            settings.setValue('minp3', QVariant(self.Set_pp3_min.toPlainText()))
            settings.setValue('maxt1', QVariant(self.Set_T1_max.toPlainText()))
            settings.setValue('mint1', QVariant(self.Set_T1_min.toPlainText()))
            settings.setValue('maxt2', QVariant(self.Set_T2_max.toPlainText()))
            settings.setValue('mint2', QVariant(self.Set_T2_min.toPlainText()))
            settings.setValue('maxt3', QVariant(self.Set_T3_max.toPlainText()))
            settings.setValue('mint3', QVariant(self.Set_T3_min.toPlainText()))

        except:
            print('setting error')


    def readSettings(self):  # 读取用户设置
        settings = QSettings('MySoft','QtPad')
        self.Set_pp1_max.setText(settings.value('maxp1'))
        self.Set_pp1_min.setText(settings.value('minp1'))
        self.Set_pp2_max.setText(settings.value('maxp2'))
        self.Set_pp2_min.setText(settings.value('minp2'))
        self.Set_pp3_max.setText(settings.value('maxp3'))
        self.Set_pp3_min.setText(settings.value('minp3'))
        self.Set_T1_max.setText(settings.value('maxt1'))
        self.Set_T1_min.setText(settings.value('mint1'))
        self.Set_T2_max.setText(settings.value('maxt2'))
        self.Set_T2_min.setText(settings.value('mint2'))
        self.Set_T3_max.setText(settings.value('maxt3'))
        self.Set_T3_min.setText(settings.value('mint3'))


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.writeSettings()


 #  自动标定函数 (自动标定按钮槽函数)
    def calibration(self):
        if self.Ser is None:
            QMessageBox.warning(self, '串口错误', '请先打开串口', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            self.mSerial.data = []  # 清空串口接收列表
            self.mSerial.start()  # 串口接收线程重新启动
            if self.calibration_quantity > 0:
                if self.CalibrationBtn.text() == '自动标定':
                    try:
                        self.calibration_quantity = int(self.quantityEdit.toPlainText())
                    except ValueError:
                        QMessageBox.warning(self, '数据错误', '请输入整数', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                    try:
                        self.calibration_times = int(self.timesEdit.toPlainText())
                    except ValueError:
                        QMessageBox.warning(self, '数据错误', '请输入整数', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                self.RunMode = 'calibration'
                self.Status.setText('标定中...')
                input_s = 'T' + 'S' + 'W'  # 'T' 为帧头，"W"为帧尾
                input_s = input_s.encode('utf-8')
                num = self.mSerial.port.write(input_s)
            else:
                pass




 #  标定完成信号的槽函数
    def calibration_finish(self,data):
        # self.RunMode = 'test'

        input_s = 'T' + 'N' + 'W'
        input_s = input_s.encode('utf_8')
        num = self.mSerial.port.write(input_s)
        # print(len(data))

        self.calibration_quantity = self.calibration_quantity - 1
        self.mSerial.data = []  # 清空串口接收列表
        if self.calibration_quantity == 0:
            self.Status.setText('标定完成')
        else:
            self.Status.setText('该转子测量完成，剩余' + str(self.calibration_quantity) + '个')
        # print(self.calibration_quantity)
        if self.calibration_quantity > 0:
            self.CalibrationBtn.setText('继续标定')
            self.calibration_data.append(data)
            QMessageBox.warning(self, '更换转子', '请更换转子', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            calibration_processeddata = []
            departeddata = []
            self.CalibrationBtn.setText('自动标定')
            self.calibration_data.append(data)
            # print(len(self.calibration_data))
            # 数据处理
            for c in self.calibration_data:  # 将三个传感器的数据分离
                d1 = c[0::3]
                departeddata.append(d1)
                d2 = c[1::3]
                departeddata.append(d2)
                d3 = c[2::3]
                departeddata.append(d3)
                calibration_processeddata.append(departeddata)  # 分离后的数据组成一个新的list
            # print(len(calibration_processeddata))
            # 处理已经分离好的数据


            # 处理每个转子的数据
            for d in calibration_processeddata:
                # 分离传感器1的数据
                pp1 = find_pp(d[0])
                pp1_ave = sum(pp1) / len(pp1)
                pp1_e = max(max(pp1) - pp1_ave, pp1_ave - min(pp1))
                pp1_max = pp1_ave + 3 * pp1_e
                pp1_min = pp1_ave - 3 * pp1_e
                # 分离传感器2的数据
                pp2 = find_pp(d[1])
                pp2_ave = sum(pp2) / len(pp2)
                pp2_e = max(max(pp2) - pp2_ave, pp2_ave - min(pp2))
                pp2_max = pp2_ave + 3 * pp2_e
                pp2_min = pp2_ave - 3 * pp2_e
                # 分离传感器3的数据
                pp3 = find_pp(d[2])
                pp3_ave = sum(pp3) / len(pp3)
                pp3_e = max(max(pp3) - pp3_ave, pp3_ave - min(pp3))
                pp3_max = pp3_ave + 3 * pp3_e
                pp3_min = pp3_ave - 3 * pp3_e

                t1 = find_period(d[0])
                t2 = find_period(d[1])
                t3 = find_period(d[2])









# 创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 第一步：创建一个创建Figure
        super(MyFigure, self).__init__(self.fig)      # 第二步：在父类中激活Figure窗口    # 此句必不可少，否则不能显示图形
        self.axes = self.fig.add_subplot(311)  # 第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
        self.axes2 = self.fig.add_subplot(312)
        self.axes3 = self.fig.add_subplot(313)
    # 第四步：就是画图，【可以在此类中画，也可以在其它类中画】



# 绘图线程(并没有)


# 串口接收线程
class SerialPort(QThread):

    #定义这个线程中会用到的信号
    DataReceiveFinish = pyqtSignal(list) # 数据接收完成信号，参数为装有数据的列表
    ReceivingData = pyqtSignal()  # 正在接收数据信号，无参数
    ReceiveCounter = pyqtSignal(int)  # 接收数据数量信号，参数为已接收的数据的数量

    calibration_finish = pyqtSignal(list)  # 标定完成信号，参数为装有数据的列表

    message = '' #暂时存储从串口读取的数据
    data = [] #存接收数据的列表

    def __init__(self, port, buand):
        super(SerialPort, self).__init__()
        self.port = serial.Serial(port, buand) #配置串口并按配置打开串口
        self.port.close() #关闭串口
        if not self.port.isOpen(): #若串口关闭，重新打开串口
            self.port.open()
    def port_open(self):
        if not self.port.isOpen():
            self.port.open()

    def port_close(self):
        self.port.close()

    def run(self): #重写串口读取线程的run方法
        while True:
            self.message = self.port.read(4)
            print(self.message)
            try:
                self.data.append(float(self.message))
            except ValueError:
                pass
            print(len(self.data))
            if mainWindow.RunMode == 'test':
                if len(self.data) == 1:
                    self.ReceivingData.emit()
                if len(self.data) >1:
                    self.ReceiveCounter.emit(len(self.data))
                if len(self.data) >= 3000:
                    print('receive data finish')
                    self.DataReceiveFinish.emit(self.data)
                    # self.sleep(2)
                    break
            if mainWindow.RunMode == 'calibration':
                if len(self.data) >= 3000*mainWindow.calibration_times:
                    self.calibration_finish.emit(self.data)
                    break




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


