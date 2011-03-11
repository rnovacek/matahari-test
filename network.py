
from module import Module, Library

class NetworkTest(Module):
    def __init__(self, qmf_object=None, dbus_object=None, lib_object=None, impl_object=None):
        Module.__init__(self, qmf_object, dbus_object, lib_object, impl_object)
    
    def check(self):
        print "Module NETWORK"
        dbus_list = self.dbus_object.list()
        qmf_list = self.qmf_object.list().outArgs['iface_map']
        self.test("list[len]", len(qmf_list), len(dbus_list))
        for i in range(len(dbus_list)):
            self.test("list[%d]" % i, dbus_list[i], qmf_list[i])
            self.test("mac[%d]" % i, self.dbus_object.get_mac_address(dbus_list[i]), self.qmf_object.get_mac_address(qmf_list[i]).outArgs['mac'])
            self.test("ip[%d]" % i, self.dbus_object.get_ip_address(dbus_list[i]), self.qmf_object.get_ip_address(qmf_list[i]).outArgs['ip'])
            self.test("status[%d]" % i, self.dbus_object.status(dbus_list[i]), self.qmf_object.status(qmf_list[i]).outArgs['status'])
        # TODO: start and stop

class NetworkLib(Library):
    def __init__(self, lib):
        Library.__init__(self, lib)

    def __getattr__(self, name):
        return getattr(self.lib, name)
