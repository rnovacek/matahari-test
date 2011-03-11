#!/usr/bin/python

import sys
from qmf.console import Session
from module import DBus
import dbus

from host import HostTest, HostLib
from network import NetworkTest, NetworkLib
from services import ServicesTest, ServicesLib

MATAHARI_PACKAGE = 'org.matahariproject'

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

### QMF

def getQMF(_class):
    try:
        return session.getObjects(_class=_class, _package=MATAHARI_PACKAGE)[0]
    except Exception as e:
        print "Unable to create QMF object (%s). QMF tests of %s module will be disabled." % (e.message, _class)
        return None
        
qmf_host = getQMF('host')
qmf_network = getQMF('network')
qmf_services = getQMF('services')

### DBus

def getDBus(obj, path, iface):
    try:
        return DBus(bus.get_object(obj, path), iface)
    except Exception as e:
        print "Unable to create DBus object (%s). DBus tests of object %s will be disabled." % (e.message, obj)
        return None
        
try:
    bus = dbus.SystemBus()
except Exception as e:
    print "Unable to connect to DBus system bus (%s). DBus tests will be disabled." % e.message
    dbus_host = dbus_network = dbus_services = None
else:
    dbus_host = getDBus('org.matahariproject.Host',
                        '/org/matahariproject/Host',
                        'org.matahariproject.Host')
    dbus_network = getDBus('org.matahariproject.Network',
                           '/org/matahariproject/Network',
                           'org.matahariproject.Network')
    dbus_services = getDBus('org.matahariproject.Services',
                            '/org/matahariproject/Services',
                            'org.matahariproject.Services')

### Libs

def getLib(obj, name):
    try:
        return obj(name)
    except Exception as e:
        print "Unable to load %s library (%s). Library test will be disabled." % (name, e.message)
        return None

lib_host = getLib(HostLib, "libmhost.so")
lib_network = getLib(NetworkLib, "libmnet.so")
lib_services = getLib(ServicesLib, "libmsrv.so")

modules = (HostTest(qmf_host, dbus_host, lib_host),
           ServicesTest(qmf_services, dbus_services, lib_services),
           NetworkTest(qmf_network, dbus_network, lib_network)
          )

for module in modules:
    module.check()

session.close()
