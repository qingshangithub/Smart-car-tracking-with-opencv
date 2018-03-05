from nn import NeuralNetwork
import pickle
from car import Car
import time
import numpy as np
import timeit


car = Car('127.0.0.1', 5555, 0.4, 0.25)

clf = pickle.load(open('svr_redict', 'rb'))

def cal_direction(img):
    x = img.flatten().reshape(-1)
    dir = clf.predict(x)
    return x
    

'''
network = NeuralNetwork(494, 10, 21, 1.2)
parameters_file_name = 'weights'
network.load_parameters(parameters_file_name)


def cal_direction(img):
    x = img.flatten().reshape(-1)
    vec = network.predict(x)
    return vec


def test_cam():
    img, raw = car.get_image_async()
    vec = img.flatten().reshape(-1)
    select = vec[np.where( vec >= 200 )]
    print(len(select))


'''
def control_loop():
    car.set_straight_speed(-1.0)
    try:
        while True:
            img, raw = car.get_image_async()
            dir_vec = cal_direction(img)
            '''
            max_index = np.argmax(dir_vec)
            bias = (max_index - 10) / 10
            '''
            bias = dir_vec[0]
            car.set_turn_bias(bias)
            time.sleep(0.03)
    finally:
        car.stop()

if __name__ == '__main__':
    control_loop()
    