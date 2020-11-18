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



class TangoApplier(object):
	"""docstring for TangoApplier"""
	def __init__(self):
		super(TangoApplier, self).__init__()

	def parse_loading_list(self, loading_list, value_list=None):
		device_list = {}
		attr_value_list = {}
		for name, path in loading_list.items():
			el = path.split('/')
			dev_name = '/'.join(el[:-1])
			attr = el[-1]
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
        dev_list, value_list = parse_loading_list(loading_list, value_list)
        for dev_name, attrs in dev_list.items():
            dev = tango.DeviceProxy(dev_name)
            #print(attrs)
            #id_ = self.dev.read_attributes_asynch(attrs)
            #timer = threading.Thread(target=self.read_end_, args=(id_, dev_name, attrs))
            id_list = {}
            for attr in attrs:
                try:
                    id_= dev.write_attribute_asynch(attr, value_list[dev_name+'/'+attr])
                    id_list[id_] = dev_name+'/'+attr
                except Exception as e:
                    self.error_list[dev_name+"/"+attr] = e
                timer = threading.Thread(target=self.save_snapshot_thread, args=(id_list, dev, dev_name))
                timer.start()

	def save_snapshot_thread(self, id_list, dev, dev_name):
		while id_list:
	        ids = [id_ for id_ in id_list.keys()]
	        for id_ in ids:
	            try:
	                dev.write_attribute_reply(id_)
	                id_list.pop(id_)
	            except tango.DevFailed as e:
	                #print(attr+"\nError!!!!!!!!!\n\n")
	                print(e.args[0].desc)
	                if e.args[0].reason == 'API_BadAsynReqType':
	                    pass
	                else:
	                    self.error_list[dev] = e
	                    id_list.pop(id_)
	        
	            except Exception as e:
	                raise e 


    def load_snapshot(self, loading_list):
        self.values = {}
        self.error_list = {}
        #self.dev = tango.DeviceProxy("sys/tg_test/1")
        dev_list = parse_loading_list(loading_list)
        for dev_name, attrs in dev_list.items():
            dev = tango.DeviceProxy(dev_name)
            print(attrs)
            #id_ = self.dev.read_attributes_asynch(attrs)
            #timer = threading.Thread(target=self.read_end_, args=(id_, dev_name, attrs))
            id_list = {}
            for attr in attrs:
                id_list[dev.read_attribute_asynch(attr)] = attr
            timer = threading.Thread(target=self.read_one_end_, args=(id_list, dev, dev_name))
            timer.start()

    def load_snapshot_thread(self, id_list, dev, dev_name):
        while id_list:
            sleep(1)
            ids = [id_ for id_ in id_list.keys()]
            for id_ in ids:
                try:
                    dev = id_list[id_]
                    data = dev.read_attribute_reply(id_)
                    self.values[dev] = data.value
                    #self.values[id_list[id_]] = data.value
                    id_list.pop(id_)
                    print(data)
                except tango.DevFailed as e:
                    print(e.args)
                    if e.args[0].reason == 'API_BadAsynReqType':
                        pass
                    else:
                        self.error_list[dev] = e
                        id_list.pop(id_)
                except Exception as e:
                    raise e             
        print(self.values)
        print(self.error_list)


if __name__ == '__main__':
	tang_app = TangoApplier()
	tang_app.save_snapshot(loading_list_, value_list)
	tang_app.load_snapshot(loading_list_)
	print(new_list)
	print(new_val_list)

