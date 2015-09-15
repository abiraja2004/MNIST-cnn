#!/usr/bin/env python3
__author__ = "F. Cagnin and A. Torcinovich"

import argparse

import numpy as np

import network


def load_mnist_dataset(dataset_path):
    # temporary function used to load the mnist data set
    import gzip
    import pickle

    with gzip.open(dataset_path, "rb") as f:
        tr_d, va_d, te_d = pickle.load(f, encoding="latin1")
        training_inputs = [np.reshape(x, (28, 28)) for x in tr_d[0]]
        training_data = zip(training_inputs, [y for y in tr_d[1]])
        validation_inputs = [np.reshape(x, (28, 28)) for x in va_d[0]]
        validation_data = zip(validation_inputs, va_d[1])
        test_inputs = [np.reshape(x, (28, 28)) for x in te_d[0]]
        test_data = zip(test_inputs, te_d[1])
        return training_data, validation_data, test_data


parser = argparse.ArgumentParser()
parser.add_argument("dataset_path")
args = parser.parse_args()

np.random.seed(314)

print("Loading data")
training_data, validation_data, test_data = load_mnist_dataset(args.dataset_path)

print("Generating desired CNN")
# vec = [784, ("cl", 5, 1, "sigmoid"), ("pl", 2, "mean"), ("fcl", 100, "sigmoid"), ("fcl", 10, "sigmoid")]
vec = [784, ("fcl", 100, "sigmoid"), ("fcl", 10, "sigmoid")]
net = network.NeuralNetwork(vec, "quadratic")

print("Training CNN")
network.train(net, list(training_data), 30, 10, 3.0)

print("Testing CNN performances")
network.test(net, list(test_data))
