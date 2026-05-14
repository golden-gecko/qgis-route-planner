class Iface:
    instance = None

    @staticmethod
    def get():
        return Iface.instance

    @staticmethod
    def set(iface):
        Iface.instance = iface