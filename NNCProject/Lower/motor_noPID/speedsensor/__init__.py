#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
monitor wheel speed via subprocess
"""

import pigpio
from multiprocessing import Process
from multiprocessing.sharedctypes import RawValue
from collections import deque
from time import sleep

# set up
left_sensor_gpio = 27
right_sensor_gpio = 17
cache_width = 3
time_out = 135
time_width_restr = 20000
# shared value
left_speed = RawValue('f', 0)
right_speed = RawValue('f', 0)
# shared lock
#ls_lock = Lock()
#rs_lock = Lock()

def init_monitor(ls, rs):
    gpio = pigpio.pi()
    gpio.set_mode(left_sensor_gpio, pigpio.INPUT)
    gpio.set_mode(right_sensor_gpio, pigpio.INPUT)
    left_edge_time_tick = gpio.get_current_tick()
    right_edge_time_tick = gpio.get_current_tick()
    left_speed_queue = deque(maxlen=cache_width)
    right_speed_queue = deque(maxlen=cache_width)

    def on_left_edge(gpio, level, tick):
        nonlocal ls,  left_speed_queue,  left_edge_time_tick
        speed = 0.0
        if len(left_speed_queue) >= cache_width:
            left_speed_queue.popleft()
        if level == pigpio.TIMEOUT:
            left_speed_queue.clear()
            left_speed_queue.append(0.0)
            ls.value = speed
        else:
            span = tick - left_edge_time_tick
            if span <= time_width_restr:
                return
            left_edge_time_tick = tick
            speed = 0.537 /(span * 20 / 1e6)
            left_speed_queue.append(speed)
        #lsl.acquire()
            ls.value = sum(left_speed_queue) / cache_width
        #lsl.release()

    def on_right_edge(gpio, level, tick):
        nonlocal rs, right_speed_queue,  right_edge_time_tick
        speed = 0.0
        if len(right_speed_queue) >= cache_width:
            right_speed_queue.popleft()
        if level == pigpio.TIMEOUT:
            right_speed_queue.clear()
            right_speed_queue.append(0.0)
            rs.value = speed
        else:
            span = tick - right_edge_time_tick
            if span <= time_width_restr:
                return
            right_edge_time_tick = tick
            speed = 0.537 /(span * 20 / 1e6)
            right_speed_queue.append(speed)
        #rsl.acquire()
            rs.value = sum(right_speed_queue) / cache_width
        #rsl.release()

    left_callback = gpio.callback(left_sensor_gpio, pigpio.RISING_EDGE, on_left_edge)
    right_callback = gpio.callback(right_sensor_gpio, pigpio.RISING_EDGE, on_right_edge)
    gpio.set_watchdog(left_sensor_gpio, time_out)
    gpio.set_watchdog(right_sensor_gpio, time_out)
    # keep alive
    while True:
        sleep(100)


process = Process(target=init_monitor, args=(left_speed, right_speed))
process.start()

if __name__ == '__main__':
    while True:
        print('left: %f, right: %f' % (left_speed.value, right_speed.value))
        sleep(0.5)



