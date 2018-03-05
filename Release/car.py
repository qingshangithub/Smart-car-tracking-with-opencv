import socket

from struct import Struct

from io import BytesIO
from threading import Thread
from queue import Queue







class Car(object):
    """
        in, get frame size
        sl , sr : synchronized set speed
        al, ar : asynchronous set speed
        gs: get speed
        sp: synchronized get picture :response 'ok'
        ap: asynchronously get picture
        ok: confirm
    """
    __slots__ = ['_ip', '_port', '_sock', 'database_pipe',
                 '_command_packer', '_single_resp_unpacker', '_double_resp_unpacker',
                 '_frame_size', '_video_thread', '_keep_streaming',
                 'turn_bias', '_straight_speed', '_speed_bound', '_dead_zone',
                 'keep_serving', 'recording']

    def __init__(self, ip_, p_, speed_bound_, dead_zone_):
        self._ip = ip_
        self._port = p_
       
        self._speed_bound = speed_bound_
        self._dead_zone = dead_zone_
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect((self._ip, self._port))
        except socket.error:
            print('Connect failed')
        print('Connected')
        self._command_packer = Struct('2s f')
        self._single_resp_unpacker = Struct('f')
        self._double_resp_unpacker = Struct('f f')
       
        self.keep_serving = False

        self._straight_speed = 0.0
        self.turn_bias = 0.0

  

    def _update_speed(self):
        straight = self._straight_speed * self._speed_bound
        bias = self.turn_bias * self._speed_bound * 0.8
        if straight < 0:  # move forward
            if bias < 0:  # turn left
                left = straight - bias if straight - bias <= 0 else 0
                right = straight + bias if straight + bias >= -self._speed_bound else -self._speed_bound
            else:
                left = straight - bias if straight - bias >= -self._speed_bound else -self._speed_bound
                right = straight + bias if straight + bias <= 0 else 0
        elif straight > 0:  # move backward
            if bias < 0:
                left = straight + bias if straight + bias >= 0 else 0
                right = straight - bias if straight - bias <= self._speed_bound else self._speed_bound
            else:
                left = straight + bias if straight + bias <= self._speed_bound else self._speed_bound
                right = straight - bias if straight - bias >= 0 else 0
        else:
            left = -bias
            right = bias
        # dead zone
        # left = left if abs(left) > self._dead_zone else 0
        # right = right if abs(right) > self._dead_zone else 0
        left_cmd = self._command_packer.pack(b'al', left)
        right_cmd = self._command_packer.pack(b'ar', right)
        self._sock.sendall(left_cmd)
        self._sock.sendall(right_cmd)

    def set_straight_speed(self, s):
        self._straight_speed = s
        self._update_speed()

    def set_turn_bias(self, b):
        self.turn_bias = b
        self._update_speed()

    def stop(self):
        self._straight_speed = 0
        self.turn_bias = 0
        self._update_speed()



if __name__ == '__main__':
    file_name = 'data'
    car = Car('192.168.1.136', 5555, 0.5, 0.25)
    car.set_straight_speed(-1)
    car.set_turn_bias(0.5)
    1
    # car.collect_data(file_name)
    # car.start_stream_video()
    # car.start_control()
