import pandas as pd
import numpy as np
import pickle
from scipy.optimize import minimize


class Layer(object):
    delta_init = 0.12

    def __init__(self, num_i, num_o):
        self.in_num = num_i
        self.out_num = num_o
        self.forward_matrix = np.matrix(np.random.uniform(-self.delta_init, self.delta_init, num_i * num_o)).reshape(
            num_o, num_i)
        self.bias = np.array(np.random.uniform(-self.delta_init, self.delta_init, num_o))


class NeuralNetwork(object):
    def __init__(self, i, j, k, lam):
        self.I_num = i
        self.J_num = j
        self.K_num = k
        self.constrain_lambda = lam
        self.layer_I = Layer(i, j)
        self.layer_J = Layer(j, k)

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    def unpack(self, long_vector):
        w_i_j = long_vector[0:(self.I_num*self.J_num)].reshape(self.J_num, self.I_num)
        b_i = long_vector[(self.I_num*self.J_num): (self.I_num*self.J_num+self.J_num)]
        w_j_k = long_vector[(self.I_num*self.J_num+self.J_num):
            (self.I_num*self.J_num+self.J_num+self.J_num*self.K_num)].reshape(self.K_num, self.J_num)
        b_j = long_vector[(self.I_num*self.J_num+self.J_num+self.J_num*self.K_num):len(long_vector)]
        return np.matrix(w_i_j), b_i, np.matrix(w_j_k), b_j

    def pack(self):
        vector = np.hstack((
            np.asarray(self.layer_I.forward_matrix).reshape(-1), self.layer_I.bias,
            np.asarray(self.layer_J.forward_matrix).reshape(-1), self.layer_J.bias)
        )
        return vector

    def predict(self, x_vec):
        x_vec = x_vec.reshape(len(x_vec), 1)
        step_one = self.sigmoid(self.layer_I.forward_matrix * x_vec + self.layer_I.bias[:, np.newaxis])
        step_two = self.sigmoid(self.layer_J.forward_matrix * step_one + self.layer_J.bias[:, np.newaxis])
        return step_two

    @staticmethod
    def cost(long_vec, x_vec, y_vec, self):
        n = self.K_num
        lamb = self.constrain_lambda
        w_i_j, b_i, w_j_k, b_j = self.unpack(long_vec)
        o_j = self.sigmoid(w_i_j * x_vec + b_i[:, np.newaxis])
        o_k = self.sigmoid(w_j_k * o_j + b_j[:, np.newaxis])
        return -1 / n * np.sum(np.multiply(y_vec,np.log(o_k)) + np.multiply((1 - y_vec), np.log(1 - o_k))) + \
               lamb / (2 * n) * (np.sum(np.multiply(w_i_j, w_i_j)) + np.sum(np.multiply(w_j_k, w_j_k)))

    @staticmethod
    def gradient(long_vec, x_vec, y_vec, self):
        n = self.K_num
        ncol = x_vec.shape[1]
        lamd = self.constrain_lambda
        w_i_j, b_i, w_j_k, b_j = self.unpack(long_vec)
        o_i = x_vec
        o_j = self.sigmoid(w_i_j * o_i + b_i[:, np.newaxis])
        o_k = self.sigmoid(w_j_k * o_j + b_j[:, np.newaxis])
        delta = -(1 / n) * (y_vec - o_k)
        partial_w_j_k = delta * o_j.T + lamd / n * w_j_k
        partial_b_j = delta * np.ones(ncol).reshape(ncol, 1)
        delta = np.multiply(w_j_k.T * delta, np.multiply(o_j, (1 - o_j)))
        partial_w_i_j = delta * o_i.T + lamd / n * w_i_j
        partial_b_i = delta * np.ones(ncol).reshape(ncol, 1)
        return np.hstack((
            np.asarray(partial_w_i_j).reshape(-1), np.asarray(partial_b_i).reshape(-1),
            np.asarray(partial_w_j_k).reshape(-1), np.asarray(partial_b_j).reshape(-1),)
        )

    @staticmethod
    def delta_gradient(long_vec,  x_vec, y_vec, self):
        epsilon = 0.005
        num = len(long_vec)
        l = []
        for i in range(0, num):
            upper = np.array(long_vec, copy=True)
            upper[i] += epsilon
            lower = np.array(long_vec, copy=True)
            lower[i] -= epsilon
            delta = self.cost(upper, x_vec, y_vec, self) - self.cost(lower, x_vec, y_vec, self)
            l.append(delta/(2*epsilon))
        return np.array(l)

    def gradient_check(self, x_vec, y_vec):
        long_vec = self.pack()
        delta_g = self.delta_gradient(long_vec, x_vec, y_vec, self)
        bp_g = self.gradient(long_vec, x_vec, y_vec, self)
        difference = bp_g - delta_g
        return difference.max()

    def bulk_train(self, x_series, y_series):
        x_list = []
        for row in x_series:
            x_list.append(row.reshape(-1))
        x_mat = np.matrix(x_list).T
        y_list = []
        for row in y_series:
            y_list.append(row.reshape(-1))
        y_mat = np.matrix(y_list).T
        long_vector = self.pack()
        result = minimize(fun=self.cost, x0=long_vector, method='L-BFGS-B', jac=self.gradient, args=(x_mat, y_mat, self))
        self.layer_I.forward_matrix, self.layer_I.bias, \
            self.layer_J.forward_matrix, self.layer_J.bias = self.unpack(result.x)

    def load_parameters(self, fn):
        long_vec = pickle.load(open(fn, 'rb'))
        w_i_j, b_i, w_j_k, b_j = self.unpack(long_vec)
        self.layer_I.forward_matrix = w_i_j
        self.layer_I.bias = b_i
        self.layer_J.forward_matrix = w_j_k
        self.layer_J.bias = b_j

    def dump_parameters(self, fn):
        pickle.dump(self.pack(), open(fn, 'wb'))

if __name__ == '__main__':
    import scipy.io

    data_frame = scipy.io.loadmat(
        'F:\MyDocuments\Documents\CourseraMaterial\Machine Learning\machine-learning-ex4\ex4\ex4data1.mat')
    img = data_frame['X']
    images = np.vsplit(img, 5000)
    image_series = pd.Series(images)

    labels = data_frame['y']
    label_list = []
    for i in range(0, 5000):
        newline = np.zeros(10, dtype='i')
        label = int(labels[i])
        if label == 10:
            newline[0] = 1
        else:
            newline[label] = 1
        label_list.append(newline)
    y_series = pd.Series(label_list)

    xs = []
    for row in image_series:
        xs.append(row.reshape(-1))
    x_matrix = np.matrix(xs).T
    ys = []
    for row in y_series:
        ys.append(row.reshape(-1))
    y_matrix = np.matrix(ys).T

    neuralnet = NeuralNetwork(400, 25, 10, 1.2)
    weights = neuralnet.pack()

    neuralnet.bulk_train(image_series, y_series)
    c = neuralnet.cost(neuralnet.pack(), x_matrix, y_matrix, neuralnet)
    print(c)
