#! /usr/bin/python3
# -*- coding: utf-8 -*-
import pigpio
from time import sleep
from threading import Thread, Event
from multiprocessing.sharedctypes import RawValue
import sys
sys.path.append('./motor_multiPro')
from speedsensor import left_speed, right_speed


class Motor(object):
    __slots__ = ('__gpio', '__PWM', '__posi', '__nega',
                 '__target_speed', '__pid_thread', 'speed_sensor','__keep_adjust', '__accept_new_speed')

    def __init__(self, posit, negat, pwm, ss_bind):
        self.__gpio = pigpio.pi()
        self.__PWM = pwm
        self.__posi = posit
        self.__nega = negat
        self.__target_speed = 0.0
        # self.__speed_lock = Lock()
        self.__accept_new_speed = Event()
        self.__accept_new_speed.set() 
        self.speed_sensor = ss_bind
        self.__keep_adjust = False
        g = self.__gpio
        g.set_mode(pwm, pigpio.OUTPUT)  # PWM
        g.set_mode(negat, pigpio.OUTPUT)  # negative
        g.set_mode(posit, pigpio.OUTPUT)  # positive
        g.write(negat, 0)
        g.write(posit, 0)
        self.__pid_thread = Thread(target=self.__pid_adjust)
        self.__pid_thread.start()

    def __get_speed(self):
        return self.speed_sensor.value

    def __update_pwm(self, s):
        pwm = int(s * 255)
        if pwm > 255:
            pwm = 255
        elif pwm < 0:
            pwm = 0
        self.__gpio.set_PWM_dutycycle(self.__PWM, pwm)

    def __pid_adjust(self):
        while True:
            self.__keep_adjust = True
            set_point = self.__target_speed
            up_func = self.__update_pwm
            gs_func = self.__get_speed
            previous_error = 0
            integral = 0
            dt = 0.008  # second
            error = 0
            self.__accept_new_speed.clear()
            while self.__keep_adjust:
                error = set_point - gs_func()
                integral += error * dt
                derivative = (error - previous_error) / dt
                out_put = 0.7 * error + 1.4 * integral - 0.10 * derivative
                print(set_point, out_put, gs_func())
                previous_error = error
                up_func(out_put)
                sleep(dt)
            self.__accept_new_speed.set()

    def change_speed(self, speed):
        g = self.__gpio
        if speed > 0.2:
            # g.set_PWM_dutycycle(self.__PWM, speed)
            g.write(self.__posi, 1)
            g.write(self.__nega, 0)
            self.__keep_adjust = False
            # self.__speed_lock.acquire()
            self.__accept_new_speed.wait()
            self.__target_speed = speed
            # self.__speed_lock.release()
        elif speed < 0.2:
            # g.set_PWM_dutycycle(self.__PWM, abs(speed))
            g.write(self.__posi, 0)
            g.write(self.__nega, 1)
            self.__keep_adjust = False
            # self.__speed_lock.acquire()
            self.__accept_new_speed.wait()
            self.__target_speed = abs(speed)
            # self.__speed_lock.release()
        else:
            g.write(self.__posi, 0)
            g.write(self.__nega, 0)

    def run(self, speed):
        self.change_speed(speed)

    def stop(self):
        g = self.__gpio
        g.write(self.__posi, 0)
        g.write(self.__nega, 0)


left_motor = Motor(19, 26, 6, left_speed)
right_motor = Motor(20, 16, 12, right_speed)
