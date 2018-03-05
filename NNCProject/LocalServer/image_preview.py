import sqlite3
import cv2
import pickle
from more_itertools import unique_everseen
from enum import Enum
import numpy as np
import pygame
from pygame.locals import *
from threading import Thread


class DataType(Enum):
    DISCRETE = 0
    CONTINUOUS = 1


class DataConn(object):
    def __init__(self, fn, dtype):
        self.data_type = dtype
        self.table_name = 'DISCRETE_TRAIN' if dtype == DataType.DISCRETE else 'CONTINUOUS_TRAIN'
        self.conn = sqlite3.connect(fn)
        self.cursor = self.conn.cursor()
        self.check_table()

    def check_table(self):
        for s in ['DISCRETE_TRAIN', 'CONTINUOUS_TRAIN']:
            self.cursor.execute('''SELECT COUNT(*) FROM sqlite_master WHERE name = ?''', (s,))
            res = self.cursor.fetchone()
            if res[0] == 0:
                self.cursor.execute('''CREATE TABLE %s
                  (ID INT PRIMARY KEY NOT NULL , IMAGE TEXT NOT NULL ,
                  RESPONSE FLOAT NOT NULL , DATE TEXT NOT NULL )''' % s)
                print('new %s table created' % s)
                self.conn.commit()
            else:
                print('%s table already exist' % s)

    def get_date_index(self):
        self.cursor.execute('''SELECT ID, DATE FROM DATA''')
        result = self.cursor.fetchall()
        dates = [r[1] for r in result]
        dates_unique = list(unique_everseen(dates))
        return dates_unique

    def get_new_chunk(self, date_s):
        self.cursor.execute('''SELECT ID, IMAGE, RESPONSE
                               FROM DATA WHERE DATE = ?''', (date_s,))
        result = self.cursor.fetchall()
        ids = [r[0] for r in result]
        image_str_seq = [r[1] for r in result]
        image_seq = [pickle.loads(s) for s in image_str_seq]
        response_seq = [r[2] for r in result]
        return ids, image_seq, response_seq

    def get_old_chunk(self, date_s):
        self.cursor.execute("SELECT ID, IMAGE, RESPONSE FROM {} WHERE DATE = '{}'".format(self.table_name, date_s))
        result = self.cursor.fetchall()
        ids = [r[0] for r in result]
        image_str_seq = [r[1] for r in result]
        image_seq = [pickle.loads(s) for s in image_str_seq]
        response_seq = [r[2] for r in result]
        return ids, image_seq, response_seq

    def save_chunk(self, ids, images, response, date):
        img_str = [pickle.dumps(i) for i in images]
        try:
            for id, img, res in zip(ids, img_str, response):
                self.cursor.execute("INSERT INTO {} (ID, IMAGE, RESPONSE, DATE) VALUES (?, ?, ?, ?)"
                                    .format(self.table_name),
                                    (id, img, res, date))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print('Duplicated insert, maybe you should try update_chunk()')

        print('saved')

    def update_chunk(self, ids, images, response, date):
        img_str = [pickle.dumps(i) for i in images]
        # remove old one
        self.cursor.execute('''DELETE FROM {} WHERE DATE = ?'''.format(self.table_name), ( date,))
        for id, img, res in zip(ids, img_str, response):
            self.cursor.execute('''INSERT INTO {} (ID, IMAGE, RESPONSE, DATE)
                VALUES (?, ?, ?, ?)'''.format(self.table_name), (id, img, res, date))
        self.conn.commit()
        print('updated')

    def dump_train_data(self, dates):
        x_list = []
        y_list = []
        for date in dates:
            self.cursor.execute("SELECT IMAGE, RESPONSE FROM {} WHERE DATE = ?".format(self.table_name), (date,))
            result = self.cursor.fetchall()
            image_str_seq = [r[0] for r in result]
            for img_str in image_str_seq:
                img = pickle.loads(img_str)
                # img = cv2.resize(img, (0, 0), fx=0.2, fy=0.2, interpolation=cv2.INTER_LINEAR)
                x_list.append(img.flatten().reshape(-1))
            responses = [r[1] for r in result]
            if self.data_type == DataType.DISCRETE:
                for res in responses:
                    y = np.zeros(21)
                    index = int(10 + 10*res)
                    y[index] = 1
                    y_list.append(y)
            else:
                y_list.extend(responses)
        print(len(x_list[0]))
        return x_list, y_list


class Selection(object):
    def __init__(self, ids_, imgs_, res_, date_):
        self.ids = ids_
        self.images = imgs_
        self.responses = res_
        self.date = date_
        self._img_dict = None
        self._response_dict = None
        self._save_dict = None
        self._selecting = False
        self._current_id_index = -1
        self._end_index = len(ids_) - 1
        self._start_index = 0
        self.cid = None
        self.cimg = None
        self.cres = None

    def _key_loop(self):
        while self._selecting:
            k = cv2.waitKey(0)
            if k == 2555904:
                self.next_image()
            elif k == 2424832:
                self.previous_image()
            elif k == 8:
                self.delete_sample()
            elif k == 13:
                self.commit_sample()
            elif k == 27:
                self.finish()
                break

    def load(self, default_select_flag):
        self._img_dict = {k: v for (k, v) in zip(self.ids, self.images)}
        self._response_dict = {k: v for (k, v) in zip(self.ids, self.responses)}
        self._save_dict = {k: default_select_flag for k in self.ids}
        id = self.ids[0]
        self._current_id_index = 0
        show = self._draw_on_image(self._img_dict[id], self._response_dict[id], self._save_dict[id])
        self._selecting = True
        cv2.imshow('image', show)
        self._key_loop()

    def next_image(self):
        if self._current_id_index < self._end_index:
            self._current_id_index += 1
            id = self.ids[self._current_id_index]
            show = self._draw_on_image(self._img_dict[id], self._response_dict[id], self._save_dict[id])
            cv2.imshow('image', show)

    def commit_sample(self):
        id = self.ids[self._current_id_index]
        self._save_dict[id] = True
        show = self._draw_on_image(self._img_dict[id], self._response_dict[id], self._save_dict[id])
        cv2.imshow('image', show)

    def delete_sample(self):
        id = self.ids[self._current_id_index]
        self._save_dict[id] = False
        show = self._draw_on_image(self._img_dict[id], self._response_dict[id], self._save_dict[id])
        cv2.imshow('image', show)

    def next_response(self):
        pass

    def previous_image(self):
        if self._current_id_index > self._start_index:
            self._current_id_index -= 1
            id = self.ids[self._current_id_index]
            show = self._draw_on_image(self._img_dict[id], self._response_dict[id], self._save_dict[id])
            cv2.imshow('image', show)

    def finish(self):
        valid_index = [i for i in self.ids if self._save_dict[i]]
        images = [self._img_dict[i] for i in valid_index]
        response = [self._response_dict[i] for i in valid_index]
        cv2.destroyAllWindows()
        self.cid = valid_index
        self.cimg = images
        self.cres = response

    def get_selected(self):
        return self.cid, self.cimg, self.cres, self.date

    @staticmethod
    def _discrete_cord(cord):
        new = float('{0:.1f}'.format(cord))
        return new

    def _draw_on_image(self, img, cord, reserve):
        width = 20
        larger = cv2.resize(img, (0, 0), fx=25, fy=25, interpolation=cv2.INTER_LINEAR)
        cv2.rectangle(larger, (310, 0), (310 + width, width), (0, ), cv2.FILLED)
        for i in range(1, 11):
            cv2.rectangle(larger, (310 - 25*i, 0), (310-25*i + width, width), (0,), cv2.FILLED)
        for i in range(1, 11):
            cv2.rectangle(larger, (310 + 25 * i, 0), (310 + 25 * i + width, width), (0,), cv2.FILLED)
        disc_cord = self._discrete_cord(cord)

        start = (int(310 + 25 * 10 * disc_cord), 0)
        end = (start[0] + width, width)
        cv2.rectangle(larger, start, end, (255,), cv2.FILLED)
        if reserve:
            cv2.rectangle(larger, (620, 460), (640, 480), (255,), cv2.FILLED)
        else:
            cv2.rectangle(larger, (0, 460), (20, 480), (255,), cv2.FILLED)
        return larger


class DiscreteSelection(Selection):
    def __init__(self, ids_, imgs_, res_, date_):
        super().__init__(ids_, imgs_, res_, date_)
        self.responses = self._discrete(res_)

    def _draw_on_image(self, img, cord, reserve):
        width = 20
        larger = cv2.resize(img, (0, 0), fx=25, fy=25, interpolation=cv2.INTER_LINEAR)
        cv2.rectangle(larger, (310, 0), (310 + width, width), (0,), cv2.FILLED)
        for i in range(1, 11):
            cv2.rectangle(larger, (310 - 25 * i, 0), (310 - 25 * i + width, width), (0,), cv2.FILLED)
        for i in range(1, 11):
            cv2.rectangle(larger, (310 + 25 * i, 0), (310 + 25 * i + width, width), (0,), cv2.FILLED)

        start = (int(310 + 25 * 10 * cord), 0)
        end = (start[0] + width, width)
        cv2.rectangle(larger, start, end, (255,), cv2.FILLED)
        if reserve:
            cv2.rectangle(larger, (620, 460), (640, 480), (255,), cv2.FILLED)
        else:
            cv2.rectangle(larger, (0, 460), (20, 480), (255,), cv2.FILLED)
        return larger

    @staticmethod
    def _discrete(bias_seq):
        new = [float('{0:.1f}'.format(i)) for i in bias_seq]
        return new

if __name__ == '__main__':
    def process_discrete():
        data_connect = DataConn('data.dat', DataType.DISCRETE)
        dates = data_connect.get_date_index()

        ids, img, res = data_connect.get_new_chunk(dates[5])
        session = DiscreteSelection(ids, img, res, dates[5])
        session.load(False)
        data_connect.save_chunk(*session.get_selected())

    def process_continuous():
        data_connect = DataConn('data.dat', DataType.CONTINUOUS)
        dates = data_connect.get_date_index()

        '''
        x, y = data_connect.dump_train_data(dates[2:9])
        pickle.dump(x, open('x.con', 'wb'))
        pickle.dump(y, open('y.con', 'wb'))
        '''

        print(dates)
        ids, img, res = data_connect.get_new_chunk(dates[0])
        session = Selection(ids, img, res, dates[0])
        session.load(False)
        data_connect.update_chunk(*session.get_selected())

    process_continuous()


