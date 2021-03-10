import usb
import usb.core
import usb.util

dev = usb.core.find(find_all=True)
if dev is None:
    raise ValueError("device not found")
else:
    print(dev)