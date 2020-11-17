from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QProgressDialog, QLabel, QTextEdit, QDialog, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt, QObject



from ApplyProgressDialog import Ui_ProgressDialog


class ProgressDialog(QDialog):
    """docstring for ProgressBar"""
    def __init__(self, loading_list, parent=None):
        super(ProgressDialog, self).__init__(parent=parent)
        self.ui = Ui_ProgressDialog()
        self.ui.setupUi(self)

        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(len(loading_list))

        self.ui.canelButton.clicked.connect(self.on_canel)

        self._init_table(loading_list)

    def _init_table(self, loading_list):
        self.ui.tableWidget.setRowCount(len(loading_list))
        for idx, (name, dev) in enumerate(loading_list.items()):
            self.ui.tableWidget.setItem(idx, 0, QTableWidgetItem(dev[0]))
            self.ui.tableWidget.setItem(idx, 1, QTableWidgetItem(dev[1]))
            self.ui.tableWidget.setItem(idx, 2, QTableWidgetItem(""))


    def on_canel(self):
        self.accept()

    def setValue(self, value):
        if value >= self.ui.progressBar.maximum():
            self.accept()
            return
        self.ui.progressBar.setValue(value)

    def set_loading_item(self, num, name, dev, attr):
    	font = self.ui.tableWidget.item(num, 0).font()
    	font.setBold(True)
    	self.ui.tableWidget.item(num, 0).setFont(font)
    	self.ui.tableWidget.item(num, 1).setFont(font)
    	self.ui.tableWidget.item(num, 2).setFont(font)

    	self.ui.tableWidget.setItem(num, 2, QTableWidgetItem("in process..."))
    	self.ui.label.setText("Sending a %s to the attribute %s of the device %s..."%(name, attr, dev))
    	#self.ui.label_2.setText("   %s..."%(dev,))


    def set_done_item(self, num):
    	font = self.ui.tableWidget.item(num, 0).font()
    	font.setBold(False)
    	self.ui.tableWidget.item(num, 0).setFont(font)
    	self.ui.tableWidget.item(num, 1).setFont(font)
    	self.ui.tableWidget.item(num, 2).setFont(font)

    	self.ui.tableWidget.item(num, 0).setBackground(Qt.gray)
    	self.ui.tableWidget.item(num, 1).setBackground(Qt.gray)
    	self.ui.tableWidget.setItem(num, 2, QTableWidgetItem("done"))


    def set_loading_error(self, num):
    	font = self.ui.tableWidget.item(num, 0).font()
    	font.setBold(False)
    	self.ui.tableWidget.item(num, 0).setFont(font)
    	self.ui.tableWidget.item(num, 1).setFont(font)
    	self.ui.tableWidget.item(num, 2).setFont(font)

    	self.ui.tableWidget.item(num, 0).setBackground(Qt.red)
    	self.ui.tableWidget.item(num, 1).setBackground(Qt.red)
    	self.ui.tableWidget.setItem(num, 2, QTableWidgetItem("error"))


class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.button = QtWidgets.QPushButton('Test', self)
        self.button.clicked.connect(self.handleButton)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.button)

    def handleButton(self):
        progBar = ProgressDialog(0, 30, self)
        progBar.show()

        #pprd.setValue(n)

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.move(500,500)
    window.show()
    sys.exit(app.exec_())