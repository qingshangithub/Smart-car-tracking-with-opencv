import socket
import cv2
import numpy as np
import pickle
from struct import Struct
# import pygame
# from pygame.locals import *
from io import BytesIO
from threading import Thread
from queue import Queue
from time import sleep
import sqlite3
import datetime
import os

# initiate pygame joystick
# pygame.init()
# pygame.joystick.init()


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
        self.database_pipe = Queue()
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
        self._sock.sendall(self._command_packer.pack(b'in', 0.0))
        fs = int(*self._single_resp_unpacker.unpack(
            self._sock.recv(self._single_resp_unpacker.size)))
        print('frame size is: %d' % fs)
        self._frame_size = fs
        self._keep_streaming = False
        self.keep_serving = False
        self.recording = False
        self._video_thread = Thread(target=self._stream_video)
        self._straight_speed = 0.0
        self.turn_bias = 0.0

    def get_image_sync(self):
        array, b = self.get_image_async()
        print('Image received, send confirm')
        self._sock.sendall(self._command_packer.pack(b'ok', 0.0))
        return array

    def get_image_async(self):
        self._sock.sendall(self._command_packer.pack(b'ap', 0.0))
        received_size = 0
        block_size = 4096
        raw_io = BytesIO()
        while True:
            s = self._sock.recv(block_size)
            received_size += len(s)
            raw_io.write(s)
            if received_size >= self._frame_size:
                break

        raw_bytes = raw_io.getvalue()
        array = pickle.loads(raw_bytes)
        return array, raw_bytes

    def _stream_video(self):
        while self._keep_streaming:
            frame, b = self.get_image_async()

            # frame = cv2.adaptiveThreshold(frame, 255,
            #                             cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10)
            # ret, frame = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            frame = cv2.resize(frame, (0, 0), fx=8, fy=8, interpolation=cv2.INTER_LINEAR)
            cv2.imshow('image', frame)
            cv2.waitKey(30)
        cv2.destroyAllWindows()

    def start_stream_video(self):
        self._keep_streaming = True
        self._video_thread.start()

    def stop_stream_video(self):
        self._keep_streaming = False
        self._video_thread.join()

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

    def start_control(self):
        # event processing
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    speed = event.value if abs(event.value) >= 0.1 else 0
                    # speed *= self._speed_bound
                    if event.axis == 1:
                        self.set_straight_speed(speed)
                    elif event.axis == 2:
                        self.set_turn_bias(speed)
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 9:
                        self.keep_serving = False
                        self._keep_streaming = False
                    elif event.button == 6:
                        self.recording = True
                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == 6:
                        self.recording = False

    @staticmethod
    def _database_server(self, fn):
        """ pipe: seq, image(pickled), tuple(res1, res2, res3)"""
        pipe = self.database_pipe
        date = str(datetime.datetime.now())
        conn = sqlite3.connect(fn)
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM sqlite_master WHERE name = ?''', ('DATA',))
        res = cursor.fetchone()
        if res[0] == 0:
            cursor.execute('''CREATE TABLE DATA
              (ID INT PRIMARY KEY NOT NULL, IMAGE TEXT NOT NULL,
              RESPONSE FLOAT NOT NULL, DATE TEXT NOT NULL )''')
            print('new table created')
            conn.commit()
        while self.keep_serving or not pipe.empty():
            if pipe.empty():
                sleep(2)
                continue
            seq, image, response = pipe.get()
            cursor.execute('''INSERT INTO DATA(ID, IMAGE, RESPONSE,
                            DATE) VALUES (?, ?, ?, ?)''', (seq, image, response, date))
            print('add: %d' % seq)
            conn.commit()
        conn.close()
        print('database thread closed')

    def collect_data(self, fn):
        data_thread = Thread(target=self._database_server, args=(self, fn + '.dat'))
        self.keep_serving = True
        last = 0
        if os.path.exists('./' + fn + '.last'):
            last = pickle.load(open(fn + '.last', 'rb'))

        def record(self_):
            nonlocal last
            while self_.keep_serving:
                frame, raw = self_.get_image_async()
                larger = cv2.resize(frame, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_LINEAR)
                response = self_.turn_bias
                if self_.recording:
                    last += 1
                    self_.database_pipe.put((last, raw, response))
                cv2.imshow('image', larger)
                cv2.waitKey(30)
            pickle.dump(last, open(fn + '.last', 'wb'))
            print('data collecting thread closed')

        collect_thread = Thread(target=record, args=(self, ))
        data_thread.start()
        collect_thread.start()


if __name__ == '__main__':
    file_name = 'data'
    car = Car('192.168.137.20', 5000, 0.4, 0.25)
    car.collect_data(file_name)
    # car.start_stream_video()
    car.start_control()
