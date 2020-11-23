from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QProgressDialog, QLabel, QTextEdit, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt, QObject

import time
from threading import Thread

#from flask import current_app
#from flask.signals import Namespace


#namespace = Namespace()

from progress_dialog import ProgressDialog
#from tango_applier import TangoApplier
from proba4 import TangoApplier


loading_list_ = {
    "var1":'sys/tg_test/1/ampli',
    "var2":'sys/tg_test/1/double_scalar0',
    "var3":'sys/tg_test/2/double_scalar0',
    "var4":'sys/tg_test/2/float_scalar'
}

loading_list_ = {
    "var1":'sys/tg_test/1/ampli',
    "var2":'sys/tg_test/1/double_scalar0',
    "var4":'sys/tg_test/1/float_scalar'
}


dev_attr_value = {
    "var1":13,
    "var2":2,
    "var4":155.12
}

loading_list_ = {
    "x1" : ("path/ttr/12/attr1"),
    "x2" : ("path/ttr/45/attr1"),
    "x3" : ("path/ttr_d/ffr/attr1"),
    "x4" : ("path/ttr_d/ff_12/attr1"),
    "x5" : ("path/ttr_d/ff_12/attr2"),
    "x6" : ("path/ttr_d/ff_12/attr3"),
    "x7" : ("/attr3"),
    "x8" : ("path/"),
    "x9" : (""),}


dev_attr_value = {
    "x1" : 12,
    "x2" : 32,
    "x3" : 11,
    "x4" : 43,
    "x5" : 133,
    "x6" : 421,
    "x7" : 13,
    "x8" : 555,
    "x9" : 55,}




class Loading(QObject):
    """docstring for Loading"""
    def __init__(self, loading_list=None, tango_applier=None, progBar=None, parent=None):
        super(Loading, self).__init__()
        self.progBar = progBar
        self.loading_list = loading_list
        self.tango_applier = tango_applier
        self.num = 0
        self.count = 0
        self.parent = parent

        #self.tango_applier.begin_writing_signal.connect(self.begin_writing)
        #self.tango_applier.end_writing_signal.connect(self.end_writing)

        #self.progBar.

        #self.progBar.forceShow()

    reading_tango_completed_signal = pyqtSignal(dict)
    tango_loading_completed_signal = pyqtSignal()


    def check_tango_loading_list(self, loading_list, value_list=None):
        fixed_loading_list = {}
        fixed_value_list = {}
        error_list = []
        for name, path in loading_list.items():
            if not path:
                #error_list.append("No path for name: "+name)
                print("no path for name:", name)
                continue

            el = path.split('/')
            dev_name = '/'.join(el[:-1])
            attr = el[-1]
            if not dev_name or not attr:
                error_list.append("No attr or dev for name "+name)
                print("no attr or dev for name:", name)
                continue
            fixed_loading_list[name] = path

            if value_list is not None:
                fixed_value_list[name] = value_list[name]
        if value_list is None:
            return fixed_loading_list, error_list

        return fixed_loading_list, fixed_value_list, error_list

    def start_read_from_tango(self, loading_list):
        self.tango_applier = TangoApplier()

        loading_list, error_list = self.check_tango_loading_list(loading_list)
        if error_list:
            error_message = "Error:\n•  "+'\n•  '.join(error_list)
            QtWidgets.QMessageBox.critical(self.parent, "Mapping failed", error_message)
            return

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
        self.tango_loading_completed_signal.connect(self.reading_tango_completed)
        #self.tango_applier.read_completed_signal.connect(self.reading_tango_completed)

        self.error_list = {}
        self.reverse_loading_list = {}
        for name, dev in loading_list.items():
            self.reverse_loading_list[dev] = name

        self.tango_applier.load_snapshot(loading_list)

    def stop_tango_snapshot_loading(self):
        self.progBar.setValue(self.count)
        self.num = 0
        self.count = 0        

    def reading_tango_completed(self):
        value_list = self.tango_applier.get_values()
        if self.num == self.count:
            msgBox = QMessageBox()
            if not self.error_list:    
                msgBox.setText("Loading completed successfully.")
            else:
                detail_txt = self._create_tango_error_text("Next variables don't sending:")
                msgBox.setText("Loading completed with errors.")
                msgBox.setDetailedText(detail_txt)

            msgBox.exec()
        print(self.reverse_loading_list)
        self.reading_tango_completed_signal.emit(value_list)



    def start_write_to_tango(self, loading_list, value_list):
        self.tango_applier = TangoApplier()

        self.num = 0
        loading_list, value_list, error_list = self.check_tango_loading_list(loading_list, value_list)
        if error_list:
            error_message = "Error:\n•  "+'\n•  '.join(error_list)
            QtWidgets.QMessageBox.critical(self.parent, "Mapping failed", error_message)
            return

        self.count = len(loading_list)
        self.progBar = ProgressDialog(loading_list)
        self.progBar.accepted.connect(self.canel_write_to_tango)
        self.progBar.show()
        self.progBar.setValue(0)

        self.tango_applier.begin_writing_signal.connect(self.begin_tango_dev_writing)
        self.tango_applier.end_writing_signal.connect(self.end_tango_dev_writing)
        self.tango_applier.stop_save_snapshot_signal.connect(self.stop_tango_snapshot_saving)
        self.tango_applier.error_signal.connect(self.tango_error)
        self.tango_loading_completed_signal.connect(self.tango_writing_completed)
        #self.tango_applier.writing_completed_signal.connect(self.tango_writing_completed)

        self.error_list = {}
        self.reverse_loading_list = {}
        for name, dev in loading_list.items():
            self.reverse_loading_list[dev] = name

        self.tango_applier.save_snapshot(loading_list, value_list)

    def begin_tango_dev_writing(self, dev):
        print(dev)
        self.progBar.set_loading_item(dev)

    def end_tango_dev_writing(self, dev):
        self.progBar.set_done_item(dev)
        self.num +=1
        self.progBar.setValue(self.num)
        if self.num == self.count:
            self.tango_loading_completed_signal.emit()

    def tango_error(self, dev, error):
        dev_name = '/'.join(dev.split('/')[:-1])
        attr = dev.split('/')[-1]
        name = self.reverse_loading_list[dev]
        self.error_list[name] = (dev_name, attr, error)
        self.progBar.set_loading_error(dev)
        self.num +=1
        self.progBar.setValue(self.num)
        if self.num == self.count:
            self.tango_loading_completed_signal.emit()

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
        #self.tango_applier.stop_save_snapshot()

    def stop_tango_snapshot_saving(self):
        self.progBar.setValue(self.count)
        self.num = 0
        self.count = 0


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
        self.loading.start_write_to_tango(loading_list_, dev_attr_value)

    def loadButton(self):
        self.loading = Loading()
        self.loading.start_read_from_tango(loading_list_)
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
