
from module import Module, Library, ImplObject

class ServicesTest(Module):
    def __init__(self, qmf_object=None, dbus_object=None, lib_object=None, impl_object=None):
        Module.__init__(self, qmf_object, dbus_object, lib_object, impl_object)
    
    def check(self):
        print "Module SERVICES"
        dbus_list = self.dbus_object.list()
        qmf_list = self.qmf_object.list().outArgs['services']
        self.test("list[len]", len(qmf_list), len(dbus_list))
        for i in range(len(dbus_list)):
            self.test("list[%d]" % i, dbus_list[i], qmf_list[i])
            # Testing takes too long, so only first few services will be tested
            if i < 5:
                self.test("status[%i]" % i, self.dbus_object.status(dbus_list[i], 0, 1), self.qmf_object.status(qmf_list[i], 0, 1).outArgs['rc'])
        # TODO: start and stop

class ServicesLib(Library):
    def __init__(self, lib):
        Library.__init__(self, lib)

    def __getattr__(self, name):
        return getattr(self.lib, name)