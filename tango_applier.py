from PyQt5.QtCore import pyqtSignal, Qt, QObject

from time import sleep
import threading


import tango
from tango import ApiUtil

loading_list_ = {
    "var1":'sys/tg_test/1/ampli',
    "var2":'sys/tg_test/1/double_scalar0',
    "var3":'sys/tg_test/2/double_scalar0',
    "var4":'sys/tg_test/2/float_scalar'
}

val_list = {
    "var1":13,
    "var2":2,
    "var3":34.7,
    "var4":155.12
}




class TangoApplier(QObject):
    """docstring for TangoApplier"""
    def __init__(self):
        super(TangoApplier, self).__init__()

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
        self.error_list = {}
        dev_list, value_list = self.parse_loading_list(loading_list, value_list)
        for dev_name, attrs in dev_list.items():
            dev = tango.DeviceProxy(dev_name)
            #print(attrs)
            #id_ = self.dev.read_attributes_asynch(attrs)
            #timer = threading.Thread(target=self.read_end_, args=(id_, dev_name, attrs))
            id_list = {}
            for attr in attrs:
                try:
                    id_= dev.write_attribute_asynch(attr, value_list[dev_name+'/'+attr])
                    self.begin_writing_signal.emit(dev_name+'/'+attr)
                    id_list[id_] = dev_name+'/'+attr
                except Exception as e:
                    self.error_list[dev_name+"/"+attr] = e
                    self.error_signal.emit(dev_name+'/'+attr, e.args[0].desc)
                timer = threading.Thread(target=self.save_snapshot_thread, args=(id_list, dev, dev_name))
                timer.start()

    def save_snapshot_thread(self, id_list, dev, dev_name):
        while id_list:
            sleep(1)
            ids = [id_ for id_ in id_list.keys()]
            for id_ in ids:
                #sleep(2)
                try:
                    dev.write_attribute_reply(id_)
                    self.end_writing_signal.emit(id_list[id_])
                    id_list.pop(id_)
                except tango.DevFailed as e:
                    #print(attr+"\nError!!!!!!!!!\n\n")
                    print(e.args[0].desc)
                    if e.args[0].reason == 'API_BadAsynReqType':
                        pass
                    else:
                        self.error_list[id_list[id_]] = e
                        self.error_signal.emit(id_list[id_], e.args[0].desc)
                        id_list.pop(id_)
            
                except Exception as e:
                    raise e 


    def load_snapshot(self, loading_list):
        self.values = {}
        self.error_list = {}
        #self.dev = tango.DeviceProxy("sys/tg_test/1")
        dev_list = self.parse_loading_list(loading_list)
        for dev_name, attrs in dev_list.items():
            dev = tango.DeviceProxy(dev_name)
            print(attrs)
            #id_ = self.dev.read_attributes_asynch(attrs)
            #timer = threading.Thread(target=self.read_end_, args=(id_, dev_name, attrs))
            id_list = {}
            for attr in attrs:
                try:
                    id_list[dev.read_attribute_asynch(attr)] = dev_name+'/'+attr
                    self.begin_writing_signal.emit(dev_name+'/'+attr)
                except Exception as e:
                    self.error_list[dev_name+'/'+attr] = e
                    self.error_signal.emit(dev_name+'/'+attr, e.args[0].desc)

            timer = threading.Thread(target=self.load_snapshot_thread, args=(id_list, dev, dev_name))
            timer.start()

    def load_snapshot_thread(self, id_list, dev, dev_name):
        while id_list:
            sleep(1)
            ids = [id_ for id_ in id_list.keys()]
            for id_ in ids:
                try:
                    #sleep(2)
                    data = dev.read_attribute_reply(id_)
                    self.values[id_list[id_]] = data.value
                    #self.values[id_list[id_]] = data.value
                    self.end_writing_signal.emit(id_list[id_])
                    id_list.pop(id_)
                    print(data)
                except tango.DevFailed as e:
                    print(e.args)
                    if e.args[0].reason == 'API_BadAsynReqType':
                        pass
                    else:
                        self.error_list[id_list[id_]] = e
                        self.error_signal.emit(id_list[id_], e.args[0].desc)
                        id_list.pop(id_)
                except Exception as e:
                    raise e             
        print(self.values)
        print(self.error_list)

    def get_values(self):
        return self.values


if __name__ == '__main__':
    tang_app = TangoApplier()
    tang_app.save_snapshot(loading_list_, value_list)
    tang_app.load_snapshot(loading_list_)
    print(new_list)
    print(new_val_list)

