#!/usr/bin/python

import sys
from pprint import pprint
from qmf.console import Console, Session
import dbus
import ctypes

MATAHARI_PACKAGE = 'org.matahariproject'

class DBus(object):
    def __init__(self, obj, iface):
        self.iface = dbus.Interface(obj, dbus_interface=iface)
        self.props = dbus.Interface(obj, dbus_interface='org.freedesktop.DBus.Properties').GetAll(iface)
    
    def __getattr__(self, name):
        if name in self.props.keys():
            return self.props[name]
        return self.iface.get_dbus_method(name)


class Library(object):
    def __init__(self, lib):
        self.lib = ctypes.CDLL(lib)

class HostLib(Library):
    def __init__(self, lib):
        Library.__init__(self, lib)
        self.d = { 'uuid', 'hostname', 'os', 'arch', 'wordsize', 'memory', 'swap', 'cpu_count', 'cpu_cores', 'cpu_model', 'cpu_flags', 'free_mem', 'free_swap', 'load', 'process_statistics' }


def test(name, *values):
    value = values[0]
    for v in values[1:]:
        if v != value:
            print "Test %s failed (" % name, value, "!=", v, ")"

class Module(object):
    def __init__(self, qmf_object, dbus_object):
        self.qmf_object = qmf_object
        self.dbus_object = dbus_object
    
    def test(self):
        raise NotImplementedError("Method test must be implemented in subclass")

class Host(Module):
    def __init__(self, qmf_object, dbus_object):
        Module.__init__(self, qmf_object, dbus_object)
    
    def test(self):
        print "Module HOST"
        test("uuid", self.qmf_object.uuid, self.dbus_object.uuid)
        test("hostname", self.qmf_object.hostname, self.dbus_object.hostname)
        test("os", self.qmf_object.os, self.dbus_object.os)
        test("arch", self.qmf_object.arch, self.dbus_object.arch)
        test("wordsize", self.qmf_object.wordsize, self.dbus_object.wordsize)
        test("memory", self.qmf_object.memory, self.dbus_object.memory)
        test("swap", self.qmf_object.swap, self.dbus_object.swap)
        test("cpu_count", self.qmf_object.cpu_count, self.dbus_object.cpu_count)
        test("cpu_cores", self.qmf_object.cpu_cores, self.dbus_object.cpu_cores)
        test("cpu_model", self.qmf_object.cpu_model, self.dbus_object.cpu_model)
        test("cpu_flags", self.qmf_object.cpu_flags, self.dbus_object.cpu_flags)
        test("cpu_model", self.qmf_object.cpu_model, self.dbus_object.cpu_model)
        test("free_mem", self.qmf_object.free_mem, self.dbus_object.free_mem)
        test("free_swap", self.qmf_object.free_swap, self.dbus_object.free_swap)
        for key in self.dbus_object.load.keys():
            test("load[%s]" % key, self.qmf_object.load[key], self.dbus_object.load[key])
        for key in self.dbus_object.process_statistics.keys():
            test("process_statistics[%s]" % key, self.qmf_object.process_statistics[key], self.dbus_object.process_statistics[key])
        
    
class Network(Module):
    def __init__(self, qmf_object, dbus_object):
        Module.__init__(self, qmf_object, dbus_object)
    
    def test(self):
        print "Module NETWORK"
        dbus_list = self.dbus_object.list()
        qmf_list = self.qmf_object.list().outArgs['iface_map']
        test("list[len]", len(qmf_list), len(dbus_list))
        for i in range(len(dbus_list)):
            test("list[%d]" % i, dbus_list[i], qmf_list[i])
            test("mac[%d]" % i, self.dbus_object.get_mac_address(dbus_list[i]), self.qmf_object.get_mac_address(qmf_list[i]).outArgs['mac'])
            test("ip[%d]" % i, self.dbus_object.get_ip_address(dbus_list[i]), self.qmf_object.get_ip_address(qmf_list[i]).outArgs['ip'])
            test("status[%d]" % i, self.dbus_object.status(dbus_list[i]), self.qmf_object.status(qmf_list[i]).outArgs['status'])
        # TODO: start and stop

class Services(Module):
    def __init__(self, qmf_object, dbus_object):
        Module.__init__(self, qmf_object, dbus_object)
    
    def test(self):
        print "Module SERVICES"
        dbus_list = self.dbus_object.list()
        qmf_list = self.qmf_object.list().outArgs['services']
        test("list[len]", len(qmf_list), len(dbus_list))
        for i in range(len(dbus_list)):
            test("list[%d]" % i, dbus_list[i], qmf_list[i])
            # Testing takes too long, so only first few services will be tested
            if i < 5:
                test("status[%i]" % i, self.dbus_object.status(dbus_list[i], 0, 1), self.qmf_object.status(qmf_list[i], 0, 1).outArgs['rc'])
        # TODO: start and stop


if len(sys.argv) < 2:
    broker = "localhost:5672"
else:
    broker = sys.argv[1]

### QMF

print "Creating session...",
sys.stdout.flush()
session = Session()
session.addBroker(broker)
print " DONE"

if MATAHARI_PACKAGE not in session.getPackages():
    print "No Matahari agent seems to be running"
    session.close()
    sys.exit(1)

qmf_host = session.getObjects(_class='host', _package=MATAHARI_PACKAGE)[0]
qmf_network = session.getObjects(_class='network', _package=MATAHARI_PACKAGE)[0]
qmf_services = session.getObjects(_class='services', _package=MATAHARI_PACKAGE)[0]

### DBus

bus = dbus.SystemBus()

dbus_host = DBus(bus.get_object('org.matahariproject.Host', '/org/matahariproject/Host'), 'org.matahariproject.Host')
dbus_network = DBus(bus.get_object('org.matahariproject.Network', '/org/matahariproject/Network'), 'org.matahariproject.Network')
dbus_services = DBus(bus.get_object('org.matahariproject.Services', '/org/matahariproject/Services'), 'org.matahariproject.Services')

###

modules = (Host(qmf_host, dbus_host),
           Services(qmf_services, dbus_services),
           Network(qmf_network, dbus_network)
          )

for module in modules:
    module.test()

session.close()
