global_iface = None


def get_iface():
    return global_iface


def set_iface(iface):
    global global_iface

    global_iface = iface
