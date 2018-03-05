#! /usr/bin/python3
# -*- coding: utf-8 -*-

from motor_noPID import left_motor, right_motor
from camera import get_frame, get_frame_size
import socket
import struct
import sys
import os


unpacker = struct.Struct('2s f')
double_packer = struct.Struct('f f')
single_packer = struct.Struct('f')


def get_packed_info():
    frame_bytes = get_frame()
    ls = left_motor.get_speed()
    rs = right_motor.get_speed()
    speeds = double_packer.pack(ls, rs)
    return frame_bytes, speeds


def session(cli, add):
    """
    sl , sr : synchronized set speed
    al, ar : asynchronous set speed
    gs: get speed
    gi: get information
    sp: synchronized get picture :response 'ok'
    ap: asynchronized get picrture
    vd: stream video
    sv: stop stream video
    """

    while True:
        command_raw = cli.recv(unpacker.size)
        name, speed = unpacker.unpack(command_raw)
        name = name.decode()
        if name[0] == 's':
            if name[1] == 'p':
                cli.sendall(get_frame())
                print('wait for response')
                res = cli.recv(unpacker.size)
                n, s = unpacker.unpack(res)
                if not n.decode() == 'ok':
                    print('send image failed')

            if name[1] == 'l':
                left_motor.change_speed(speed)
                cli.sendall(single_packer.pack(left_motor.get_speed()))
            elif name[1] == 'r':
                right_motor.change_speed(speed)
                cli.sendall(single_packer.pack(right_motor.get_speed()))
        elif name[0] == 'a':
            if name[1] == 'p':
                fb = get_frame()
                cli.sendall(fb)
            if name[1] == 'l':
                left_motor.change_speed(speed)
            elif name[1] == 'r':
                right_motor.change_speed(speed)
        elif name[0] == 'g':
            if name[1] == 's':
                cli.sendall(double_packer.pack(left_motor.get_speed(), right_motor.get_speed()))
            elif name[1] == 'i':
                fbs, speeds = get_packed_info()
                cli.sendall(fbs)
                cli.sendall(speeds)
        elif name == 'in':
            size = get_frame_size()
            picked = single_packer.pack(size)
            cli.sendall(picked)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('0.0.0.0', 5555))
    print('binded')
except socket.error as meg:
    print('Bind failed ' + str(meg))
    sys.exit()
s.listen(2)
while True:
    client, address = s.accept()
    print('connected')
    try:
        session(client, address)
    finally:
        s.close()
        os._exit(0)
