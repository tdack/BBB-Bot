# System modules
from multiprocessing import Process as Process
from multiprocessing import Queue as Queue
from SharpIR import SharpIR as SharpIR
from time import sleep

IR = SharpIR("P9_36", scale=1560.0/560.0, coeff=26.686363, power=-1.162602)

def getDistance(qin, qout):
    while qin.get() != None:
        sleep(0.5)
        qout.put(IR.distance())
    return

qin = Queue()
qout = Queue()
p = Process(target=getDistance, args=(qin, qout,) )
p.start()
for x in range(100):
    qin.put('Measure')
    distance = qout.get()
    print distance
    if distance == -1:
        break
    elif distance < 30:
        print "Taking evasive action"
        sleep(2)

qin.close()
qout.close()

