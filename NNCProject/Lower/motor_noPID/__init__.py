#! /usr/bin/python3
# -*- coding: utf-8 -*-
import pigpio
from time import sleep


class Motor(object):
    __slots__ = ('__gpio', '__PWM', '__posi', '__nega')

    def __init__(self, posit, negat, pwm):
        self.__gpio = pigpio.pi()
        self.__PWM = pwm
        self.__posi = posit
        self.__nega = negat
        g = self.__gpio
        g.set_mode(pwm, pigpio.OUTPUT)  # PWM
        g.set_mode(negat, pigpio.OUTPUT)  # negative
        g.set_mode(posit, pigpio.OUTPUT)  # positive
        g.set_PWM_frequency(pwm, 100)
        g.write(negat, 0)
        g.write(posit, 0)

    def change_speed(self, speed):
        speed = int(speed*255)
        g = self.__gpio
        if speed > 0:
            g.set_PWM_dutycycle(self.__PWM, speed)
            g.write(self.__posi, 1)
            g.write(self.__nega, 0)
        elif speed < 0:
            g.set_PWM_dutycycle(self.__PWM, abs(speed))
            g.write(self.__posi, 0)
            g.write(self.__nega, 1)
        else:
            g.write(self.__posi, 0)
            g.write(self.__nega, 0)

    def run(self, speed):
        self.change_speed(speed)

    def stop(self):
        g = self.__gpio
        g.write(self.__posi, 0)
        g.write(self.__nega, 0)


left_motor = Motor(19, 26, 6)
right_motor = Motor(20, 16, 12)
