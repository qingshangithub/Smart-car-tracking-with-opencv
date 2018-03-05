import sqlite3
import pickle
import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.cross_validation import train_test_split
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Queue

conn = sqlite3.connect('data.dat')
cursor = conn.cursor()

cursor.execute("SELECT IMAGE, RESPONSE FROM TRAIN")
result = cursor.fetchall()
image = [pickle.loads(r[0]).reshape(-1) for r in result]
response = [r[1] for r in result]
x_train, x_test, y_train, y_test = train_test_split(image, response,
                                                    test_size=0.2, random_state=0)

range_c = (1, 1000)
range_gamma = (1/494, 10)
iter_round = 10
cs = []
gammas = []
variances = []
biases = []
data_queue = Queue(maxsize=iter_round^2+1)


def generate_parameter():
    for i in range(0, iter_round):
        c = (range_c[1] - range_c[0])/iter_round + range_c[0]
        for j in range(0, iter_round):
            g = (range_gamma[1] - range_gamma[0])/iter_round + range_gamma[0]
            yield c, g


# vectors
def cost(x, y):
    x_array = np.array(x)
    y_array = np.array(y)
    square = x_array.dot(y_array)
    return square/y_array.shape[0]


def calcu(c, gamma, x_tr, y_tr, x_te, y_te, queue):
    clf = SVR(C=c, epsilon=0.05, kernel='rbf', gamma=gamma, shrinking=True)
    clf.fit(x_tr, y_tr)
    var = cost(clf.predict(x_tr), y_tr)
    bias = cost(clf.predict(x_te), y_te)
    queue.put((c, gamma, var, bias))
    print('c: %f', 'gamma: %f' % (c,gamma))


with ProcessPoolExecutor(max_workers=4) as executor:
    for c, gamma in generate_parameter():
        executor.submit(calcu, c, gamma, x_train, y_train, x_test, y_test,
                       data_queue)

