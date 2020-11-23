from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QProgressDialog, QLabel, QTextEdit, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt, QObject

import time
from threading import Thread

from random import randint

#from flask import current_app
#from flask.signals import Namespace


#namespace = Namespace()

from progress_dialog import ProgressDialog


var_list = {
    "x1" : ("path/ttr/12/attr1"),
    "x2" : ("path/ttr/45/attr1"),
    "x3" : ("path/ttr_d/ffr/attr1"),
    "x4" : ("path/ttr_d/ff_12/attr1"),
    "x5" : ("path/ttr_d/ff_12/attr2"),
    "x6" : ("path/ttr_d/ff_12/attr3"),
    "x7" : ("/attr3"),
    "x8" : ("path/"),}

dev_attr_value = {
    "x1" : 12,
    "x2" : 32,
    "x3" : 11,
    "x5" : 133,
    "x6" : 421,}


{
    "x7" : ("path/ttr_x/asd","attr1"),
    "x8" : ("path/ttr_x/my_val","attr_1"),
    "x9" : ("path/ttr_x/fdi_1","attr_12"),
    "x10" : ("path/ttr_x/fdi_2", "attr_3")

}
dev_attr_value = [12, 32, 11, 24, 133, 421, 14, 13, 121, 777, 14]

"""dev_attr_value = {
    "var1":13,
    "var2":2,
    "var3":34.7,
    "var4":155.12
}"""

class TangoApplier(QObject):
    """docstring for TangoApplier"""
    def __init__(self, loading_list=None):
        super(TangoApplier, self).__init__()
        self.loading_list = loading_list

    begin_writing_signal = pyqtSignal(str)
    end_writing_signal = pyqtSignal(str)
    stop_save_snapshot_signal = pyqtSignal()
    stop_load_snapshot_signal = pyqtSignal()
    writing_completed_signal = pyqtSignal()
    read_completed_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str, str)


    def parse_loading_list(self, loading_list, value_list=None):
        device_list = {}
        attr_value_list = {}
        for name, path in loading_list.items():
            if not path:
                print("not path for name:", name)
                continue

            el = path.split('/')
            dev_name = '/'.join(el[:-1])
            attr = el[-1]
            if not dev_name or not attr:
                print("not attr or dev for name:", name)
                continue

            if not dev_name in device_list:
                device_list[dev_name] = []
            device_list[dev_name].append(attr)

            if value_list is not None:
                attr_value_list[path] = value_list[name]
        if value_list is None:
            return device_list

        return device_list, attr_value_list


    def save_snapshot(self, loading_list, value_list):
        self.dev_list, value_list = self.parse_loading_list(loading_list, value_list)
        self.th = Thread(target=self.save_snapshot_thread)
        self.stop_thread = False
        self.th.start()

    def stop_save_snapshot(self):
        self.stop_thread = True

    def save_snapshot_thread(self):
        num = 0
        for dev_name, attrs in self.dev_list.items():
            for attr in attrs:
                dev = dev_name+'/'+attr
                if num == 4 or num == 6:
                    print("Error!")
                    num += 1
                    self.error_signal.emit(dev, "Error!")
                    continue
                if self.stop_thread:
                    self.stop_save_snapshot_signal.emit()
                    break
                self.begin_writing_signal.emit(dev)
                self.write()
                self.end_writing_signal.emit(dev)
                num += 1
        #self.dev_list = None
        self.stop_thread = False
        self.writing_completed_signal.emit()

    def write(self):
        #for x in range(90000000):
        #        pass
        time.sleep(randint(1, 3))

    def load_snapshot(self, loading_list):
        self.dev_list = self.parse_loading_list(loading_list)
        self.value_list = {}
        self.th = Thread(target=self.load_snapshot_thread)
        self.stop_thread = False
        self.th.start()

    def load_snapshot_thread(self):
        num = 0
        for dev_name, attrs in self.dev_list.items():
            for attr in attrs:
                dev = dev_name+'/'+attr
                if num == 4 or num == 6:
                    self.error_signal.emit(dev, "Error!")
                    num += 1
                    continue
                if self.stop_thread:
                    self.stop_load_snapshot_signal.emit()
                    break
                self.begin_writing_signal.emit(dev)
                val = self.read(dev, num)
                self.value_list[dev] = val
                self.end_writing_signal.emit(dev)
                num += 1
        #self.dev_list = None
        self.stop_thread = False
        self.read_completed_signal.emit(self.value_list)

    def read(self, dev, num):
        #for x in range(90000000):
        #        pass
        time.sleep(randint(1, 3))
        return dev_attr_value[num]

    def get_values(self):
        return self.value_list



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
        self.reverse_loading_list = {}
        for name, dev in loading_list.items():
            self.reverse_loading_list[dev] = name

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
        self.reverse_loading_list = {}
        for name, dev in loading_list.items():
            self.reverse_loading_list[dev] = name

        self.tango_applier.save_snapshot(loading_list)

    def begin_tango_dev_writing(self, dev):
        print(dev)
        self.progBar.set_loading_item(dev)

    def end_tango_dev_writing(self, dev):
        self.progBar.set_done_item(dev)
        self.num +=1
        self.progBar.setValue(self.num)

    def tango_error(self, dev, error):
        dev_name = '/'.join(dev.split('/')[:-1])
        attr = dev.split('/')[-1]
        name = self.reverse_loading_list[dev]
        self.error_list[name] = (dev_name, attr, error)
        self.progBar.set_loading_error(dev)
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