
import ctypes
import dbus
import subprocess

class Module(object):
    def __init__(self, qmf_object=None, dbus_object=None, lib_object=None, impl_object=None):
        self.qmf_object = qmf_object
        self.dbus_object = dbus_object
        self.lib_object = lib_object
        self.impl_object = impl_object
    
    def check(self):
        raise NotImplementedError("Method test must be implemented in subclass")

    def test(self, name, *values):
        # Ignore all None values
        vals = []
        for v in values:
            if v is not None:
                vals.append(v)
        # Test the rest
        value = vals[0]
        for v in vals[1:]:
            if v != value:
                print "Test %s failed (" % name, value, "!=", v, ")"

class Library(object):
    def __init__(self, lib):
        self.lib = ctypes.CDLL(lib)


class DBus(object):
    def __init__(self, obj, iface):
        self.iface = dbus.Interface(obj, dbus_interface=iface)
        self.props = dbus.Interface(obj, dbus_interface='org.freedesktop.DBus.Properties').GetAll(iface)
    
    def __getattr__(self, name):
        if name in self.props.keys():
            return self.props[name]
        return self.iface.get_dbus_method(name)

class ImplObject(object):
    def _readFile(self, fileName):
        f = open(fileName)
        s = f.readlines()
        f.close()
        return s

    def _readOut(self, process):
        p = subprocess.Popen(process, stdout=subprocess.PIPE)
        return p.communicate()[0].strip()
