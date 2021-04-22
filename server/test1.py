from core.timer import Timer

import time

timer = Timer("hahaha")




a = list(range(100000))
b = list(range(100000))


timer.start()
for i in a:
    pass
    for j in b:
        pass

    b.pop(0)    

timer.stop()