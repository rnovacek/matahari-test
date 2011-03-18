#!/usr/bin/python

import sys
import qmf2
import cqpid
from module import DBus
import dbus

from host import HostTest, HostLib
from network import NetworkTest, NetworkLib
from services import ServicesTest, ServicesLib

MATAHARI_PACKAGE = 'org.matahariproject'

if len(sys.argv) < 2:
    broker = "localhost:49000"
else:
    broker = sys.argv[1]

### QMF connection

print "Creating session...",
sys.stdout.flush()
connection = cqpid.Connection(broker)
connection.open()
session = qmf2.ConsoleSession(connection)
session.open()
print " DONE"

### QMF agents

qmf_host = qmf_network = qmf_services = None
for agent in session.getAgents():
    tokens = agent.getName().split(":")
    if len(tokens) >= 2 and tokens[0] == MATAHARI_PACKAGE:
        if tokens[1] == "host":
            qmf_host = agent
        elif tokens[1] == "net":
            qmf_network = agent
        elif tokens[1] == "service":
            qmf_services = agent

if qmf_host is None:
    print "Unable to create host QMF object. Tests of QMF part of host module will be disabled."
if qmf_network is None:
    print "Unable to create network QMF object. Tests of QMF part of network module will be disabled."
if qmf_services is None:
    print "Unable to create services QMF object. Tests of QMF part of services module will be disabled."

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
