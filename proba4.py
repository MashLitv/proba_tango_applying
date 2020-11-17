from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QProgressDialog, QLabel, QTextEdit, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt, QObject

import time
from threading import Thread

#from flask import current_app
#from flask.signals import Namespace


#namespace = Namespace()

from proba5 import ProgressDialog


var_list = {
    "x1" : ("path/ttr/12","attr1"),
    "x2" : ("path/ttr/45","attr1"),
    "x3" : ("path/ttr_d/ffr","attr1"),
    "x4" : ("path/ttr_d/ff_12","attr1"),
    "x5" : ("path/ttr_d/ff_12","attr2"),
    "x6" : ("path/ttr_d/ff_12","attr3"),}

dev_attr_value = {
    "x1" : 12,
    "x2" : 32,
    "x3" : 11,
    "x4" : 24,
    "x5" : 133,
    "x6" : 421,}


{
    "x7" : ("path/ttr_x/asd","attr1"),
    "x8" : ("path/ttr_x/my_val","attr_1"),
    "x9" : ("path/ttr_x/fdi_1","attr_12"),
    "x10" : ("path/ttr_x/fdi_2", "attr_3")

}

class TangoApplier(QObject):
    """docstring for TangoApplier"""
    def __init__(self, loading_list=None):
        super(TangoApplier, self).__init__()
        self.loading_list = loading_list

    begin_writing_signal = pyqtSignal(str, str, str)
    end_writing_signal = pyqtSignal(str, str, str)
    stop_save_snapshot_signal = pyqtSignal()
    stop_load_snapshot_signal = pyqtSignal()
    writing_completed_signal = pyqtSignal()
    read_completed_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str, str, str, str)

    def save_snapshot(self, loading_list):
        self.loading_list = loading_list
        self.th = Thread(target=self.save_snapshot_thread)
        self.stop_thread = False
        self.th.start()

    def stop_save_snapshot(self):
        self.stop_thread = True

    def save_snapshot_thread(self):
        for name, dev in self.loading_list.items():
            if name == "x4" or name == "x6":
                self.error_signal.emit(name, dev[0], dev[1], "Error!")
                continue
            if self.stop_thread:
                self.stop_save_snapshot_signal.emit()
                break
            self.begin_writing_signal.emit(name, dev[0], dev[1])
            self.write()
            self.end_writing_signal.emit(name, dev[0], dev[1])
        #self.loading_list = None
        self.stop_thread = False
        self.writing_completed_signal.emit()

    def write(self):
        for x in range(90000000):
                pass
        #time.sleep(1)     

    def load_snapshot(self, loading_list):
        self.loading_list = loading_list
        self.value_list = {}
        self.th = Thread(target=self.load_snapshot_thread)
        self.stop_thread = False
        self.th.start()

    def load_snapshot_thread(self):
        for name, dev in self.loading_list.items():
            if name == "x4" or name == "x6":
                self.error_signal.emit(name, dev[0], dev[1], "Error!")
                continue
            if self.stop_thread:
                self.stop_load_snapshot_signal.emit()
                break
            self.begin_writing_signal.emit(name, dev[0], dev[1])
            val = self.read(name)
            self.value_list[name] = val
            self.end_writing_signal.emit(name, dev[0], dev[1])
        #self.loading_list = None
        self.stop_thread = False
        self.read_completed_signal.emit(self.value_list)

    def read(self, name):
        for x in range(90000000):
                pass
        return dev_attr_value[name]
        #time.sleep(1) 



class Loading(QObject):
    """docstring for Loading"""
    def __init__(self, loading_list=None, tango_applier=None, progBar=None):
        super(Loading, self).__init__()
        self.progBar = progBar
        self.loading_list = loading_list
        self.tango_applier = tango_applier
        self.num = 0
        self.count = 0

        #self.tango_applier.begin_writing_signal.connect(self.begin_writing)
        #self.tango_applier.end_writing_signal.connect(self.end_writing)

        #self.progBar.

        #self.progBar.forceShow()

    reading_tango_completed_signal = pyqtSignal(dict)

    def start_read_from_tango(self, loading_list):
        self.tango_applier = TangoApplier()

        self.num = 0
        self.count = len(loading_list)
        self.progBar = ProgressDialog(loading_list)
        self.progBar.accepted.connect(self.canel_write_to_tango)
        #self.progBar.stopButton.clicked.connect(self.stop_ta)
        self.progBar.show()
        self.progBar.setValue(0)

        self.tango_applier.begin_writing_signal.connect(self.begin_tango_dev_writing)
        self.tango_applier.end_writing_signal.connect(self.end_tango_dev_writing)
        self.tango_applier.stop_load_snapshot_signal.connect(self.stop_tango_snapshot_loading)
        self.tango_applier.error_signal.connect(self.tango_error)
        self.tango_applier.read_completed_signal.connect(self.reading_tango_completed)

        self.error_list = {}

        self.tango_applier.load_snapshot(loading_list)

    def stop_tango_snapshot_loading(self):
        self.progBar.setValue(self.count)
        self.num = 0
        self.count = 0        

    def reading_tango_completed(self, value_list):
        if self.num == self.count:
            msgBox = QMessageBox()
            if not self.error_list:    
                msgBox.setText("Loading completed successfully.")
            else:
                detail_txt = self._create_tango_error_text("Next variables don't sending:")
                msgBox.setText("Loading completed with errors.")
                msgBox.setDetailedText(detail_txt)

            msgBox.exec()
        self.reading_tango_completed_signal.emit(value_list)



    def start_write_to_tango(self, loading_list):
        self.tango_applier = TangoApplier()

        self.num = 0
        self.count = len(loading_list)
        self.progBar = ProgressDialog(loading_list)
        self.progBar.accepted.connect(self.canel_write_to_tango)
        self.progBar.show()
        self.progBar.setValue(0)

        self.tango_applier.begin_writing_signal.connect(self.begin_tango_dev_writing)
        self.tango_applier.end_writing_signal.connect(self.end_tango_dev_writing)
        self.tango_applier.stop_save_snapshot_signal.connect(self.stop_tango_snapshot_saving)
        self.tango_applier.error_signal.connect(self.tango_error)
        self.tango_applier.writing_completed_signal.connect(self.tango_writing_completed)

        self.error_list = {}

        self.tango_applier.save_snapshot(loading_list)

    def begin_tango_dev_writing(self, name, dev, attr):
        self.progBar.set_loading_item(self.num, name, dev, attr)

    def end_tango_dev_writing(self, name, dev, attr):
        self.progBar.set_done_item(self.num)
        self.num +=1
        self.progBar.setValue(self.num)

    def tango_error(self, name, dev, attr, error):
        self.error_list[name] = (dev, attr, error)
        self.progBar.set_loading_error(self.num)
        self.num +=1
        self.progBar.setValue(self.num)

    def tango_writing_completed(self):
        if self.num == self.count:
            msgBox = QMessageBox()
            if not self.error_list:    
                msgBox.setText("Sending completed successfully.")
            else:
                detail_txt = self._create_tango_error_text("Next variables don't sending:")
                msgBox.setText("Sending completed with errors.")
                msgBox.setDetailedText(detail_txt)

            msgBox.exec()

    def _create_tango_error_text(self, text):
        error_msg = text
        for name, inf in self.error_list.items():
            dev_name, dev_attr, error = inf
            error_msg += ("\n•  Variable name: %s\n    Device name: %s"%(name, dev_name)+
                         "\n    Attribute name: %s\n    Reason: %s\n"%(dev_attr, error))
        return error_msg


    def canel_write_to_tango(self):
        print("stop!")
        self.tango_applier.stop_save_snapshot()

    def stop_tango_snapshot_saving(self):
        self.progBar.setValue(self.count)
        self.num = 0
        self.count = 0

"""class ProgressDialog(QProgressDialog):
    def __init__(self, labelText, cancelButtonText, minimum, maximum, parent=None):
        super(ProgressDialog, self).__init__(labelText, cancelButtonText, minimum, maximum, parent)

        #self.ui = Ui_ProgressDialog()
        #self.ui.setupUi(self)

        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(500, 400)

        self.dirNameEdit = QtWidgets.QTextEdit(self)
        self.dirNameEdit.setGeometry(QtCore.QRect(10, 30, 341, 70))
        self.dirNameEdit.setObjectName("dirNameEdit")

        self.setLabel(QLabel("text1\ntext2\ntext3"))
        self.setMinimumDuration(1)
        self.setWindowTitle("Please Wait") """


class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.load_button = QtWidgets.QPushButton('Load', self)
        self.load_button.clicked.connect(self.loadButton)

        self.save_button = QtWidgets.QPushButton('Save', self)
        self.save_button.clicked.connect(self.saveButton)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_button)

    def saveButton(self):
        self.loading = Loading()
        self.loading.start_write_to_tango(var_list)

    def loadButton(self):
        self.loading = Loading()
        self.loading.start_read_from_tango(var_list)
        self.loading.reading_tango_completed_signal.connect(self.reading_completed)

    def reading_completed(self, value_list):
        for name, val in value_list.items():
            print(name, val)

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.move(500,500)
    window.show()
    sys.exit(app.exec_())