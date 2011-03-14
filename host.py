
from ctypes import Structure, c_double, c_uint64, byref, POINTER, c_char_p
import subprocess

from module import Module, Library


class HostTest(Module):
    def __init__(self, qmf_object=None, dbus_object=None, lib_object=None, impl_object=None):
        Module.__init__(self, qmf_object, dbus_object, lib_object, impl_object)

    def check(self):
        print "Module HOST"
        self.test("uuid", 
                  self.qmf_object.uuid, 
                  self.dbus_object.uuid,
                  self.lib_object.host_get_uuid())
        self.test("hostname", 
                  self.qmf_object.hostname, 
                  self.dbus_object.hostname,
                  self.lib_object.host_get_hostname())
        self.test("os", 
                  self.qmf_object.os, 
                  self.dbus_object.os,
                  self.lib_object.host_get_operating_system())
        self.test("arch", 
                  self.qmf_object.arch, 
                  self.dbus_object.arch,
                  self.lib_object.host_get_architecture())
        self.test("wordsize", 
                  self.qmf_object.wordsize, 
                  self.dbus_object.wordsize,
                  self.lib_object.host_get_cpu_wordsize())
        self.test("memory", 
                  self.qmf_object.memory, 
                  self.dbus_object.memory,
                  self.lib_object.host_get_memory())
        self.test("swap", 
                  self.qmf_object.swap, 
                  self.dbus_object.swap,
                  self.lib_object.host_get_swap())
        self.test("cpu_count", 
                  self.qmf_object.cpu_count, 
                  self.dbus_object.cpu_count,
                  self.lib_object.host_get_cpu_count())
        self.test("cpu_cores", 
                  self.qmf_object.cpu_cores, 
                  self.dbus_object.cpu_cores,
                  self.lib_object.host_get_cpu_number_of_cores())
        self.test("cpu_model", 
                  self.qmf_object.cpu_model, 
                  self.dbus_object.cpu_model,
                  self.lib_object.host_get_cpu_model())
        self.test("cpu_flags", 
                  self.qmf_object.cpu_flags, 
                  self.dbus_object.cpu_flags,
                  self.lib_object.host_get_cpu_flags())
        self.test("free_mem", 
                  self.qmf_object.free_mem, 
                  self.dbus_object.free_mem,
                  self.lib_object.host_get_mem_free())
        self.test("free_swap", 
                  self.qmf_object.free_swap, 
                  self.dbus_object.free_swap,
                  self.lib_object.host_get_swap_free())
        for key in self.dbus_object.load.keys():
            self.test("load[%s]" % key, self.qmf_object.load[key], self.dbus_object.load[key])
        for key in self.dbus_object.process_statistics.keys():
            self.test("process_statistics[%s]" % key, self.qmf_object.process_statistics[key], self.dbus_object.process_statistics[key])

  
class HostLib(Library):
    def __init__(self, lib):
        Library.__init__(self, lib)

    def host_get_load_averages(self):
        class Sigar_loadavg_t(Structure):
            _fields_ = [('loadavg', c_double * 3)]
        self.lib.host_get_load_averages.argtype = POINTER(Sigar_loadavg_t)
        data = Sigar_loadavg_t()
        self.lib.host_get_load_averages(byref(data))
        return { 1: data.loadavg[0], 
                 5: data.loadavg[1], 
                15: data.loadavg[2] }

    def host_get_processes(self):
        class Sigar_proc_stat_t(Structure):
            _fields_ = [('total', c_uint64),
                        ('sleeping', c_uint64),
                        ('running', c_uint64),
                        ('zombie', c_uint64),
                        ('stopped', c_uint64),
                        ('idle', c_uint64),
                        ('threads', c_uint64),
                       ]

        self.lib.host_get_load_averages.argtype = POINTER(Sigar_proc_stat_t)
        data = Sigar_proc_stat_t()
        self.lib.host_get_processes(byref(data))
        return { 'total': data.total,
                 'sleeping': data.sleeping,
                 'running': data.running,
                 'zombie': data.zombie,
                 'stopped': data.stopped,
                 'idle': data.idle,
                 'threads': data.threads }
     
    def host_get_uuid(self):
        self.lib.host_get_uuid.restype = c_char_p
        return self.lib.host_get_uuid()

    def host_get_hostname(self):
        self.lib.host_get_hostname.restype = c_char_p
        return self.lib.host_get_hostname()

    def host_get_operating_system(self):
        self.lib.host_get_operating_system.restype = c_char_p
        return self.lib.host_get_operating_system()

    def host_get_architecture(self):
        self.lib.host_get_architecture.restype = c_char_p
        return self.lib.host_get_architecture()

    def host_get_cpu_model(self):
        self.lib.host_get_cpu_model.restype = c_char_p
        return self.lib.host_get_cpu_model()

    def host_get_cpu_flags(self):
        self.lib.host_get_cpu_flags.restype = c_char_p
        return self.lib.host_get_cpu_flags()

    def __getattr__(self, name):
        return getattr(self.lib, name)

class HostImpl(object):
    def __init__(self):
        pass

    def readFile(self, fileName):
        f = open(fileName)
        s = f.readline().strip()
        f.close()
        return s

    def readOut(self, process):
        p = subprocess.Popen(process, stdout=subprocess.PIPE)
        return p.communicate()[0].strip()

    def uuid(self):
        return self.readFile('/var/lib/dbus/machine-id')
        
    def hostname(self):
        return self.readOut('hostname')
    
if __name__ == '__main__':
    host = HostImpl()
    print host.uuid()
    print host.hostname()