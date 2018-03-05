import pigpio
from time import sleep
from multiprocessing import Process

p = pigpio.pi()
p.set_mode(17, pigpio.INPUT)

def cbf(g, l, tick):
    print(tick)

cb = p.callback(17, pigpio.RISING_EDGE, cbf)
if __name__ == '__main__':
    sleep(20)
