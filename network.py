
from module import Module, Library, ImplObject

class NetworkTest(Module):
    def __init__(self, qmf_object=None, dbus_object=None, lib_object=None, impl_object=None):
        Module.__init__(self, qmf_object, dbus_object, lib_object, impl_object)
    
    def check(self):
        print "Module NETWORK"
        dbus_list = self.dbus_object.list()
        qmf_list = self.qmf_object.list().outArgs['iface_map']
        self.test("list[len]", len(qmf_list), len(dbus_list))
        for i in range(len(dbus_list)):
            self.test("list[%d]" % i,
                      dbus_list[i],
                      qmf_list[i])
            self.test("mac[%d]" % i,
                      self.dbus_object.get_mac_address(dbus_list[i]),
                      self.qmf_object.get_mac_address(qmf_list[i]).outArgs['mac'])
            self.test("ip[%d]" % i,
                      self.dbus_object.get_ip_address(dbus_list[i]),
                      self.qmf_object.get_ip_address(qmf_list[i]).outArgs['ip'])
            self.test("status[%d]" % i,
                      self.dbus_object.status(dbus_list[i]),
                      self.qmf_object.status(qmf_list[i]).outArgs['status'])
            # TODO: start and stop

class NetworkLib(Library):
    def __init__(self, lib):
        Library.__init__(self, lib)

    def __getattr__(self, name):
        return getattr(self.lib, name)

class NetworkImpl(ImplObject):
    def __init__(self):
        pass
    
    def list_(self):
        s = self._readOut(["ifconfig", "-a"])
        ifaces = []
        
        for line in s.split("\n"):
            if len(line.strip()) != 0 and not line.startswith(" "):
                ifaces.append(line.split(" ")[0])
        return ifaces
    
    def get_ip_address(self, iface):
        s = self._readOut(["ifconfig", "-a"])
        good_iface = False
        for line in s.split("\n"):
            if len(line.strip()) != 0 and not line.startswith(" "):
                good_iface = (line.split(" ")[0] == iface)
            if good_iface and "inet" in line:
                for token in line.split(" "):
                    if token.startswith("addr"):
                        return token.partition(":")[2]
        return "0.0.0.0"

    def get_mac_address(self, iface):
        s = self._readOut(["ifconfig", "-a"])
        for line in s.split("\n"):
            if len(line.strip()) != 0 and not line.startswith(" "):
                tokens = line.split()
                if len(tokens) > 4 and tokens[0] == iface:
                    return tokens[4]
        return "00:00:00:00:00:00"

if __name__ == '__main__':
    net = NetworkImpl()
    for iface in net.list_():
        print iface, net.get_ip_address(iface), net.get_mac_address(iface)
        