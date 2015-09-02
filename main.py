#!/usr/bin/env python3
__author__ = "F. Cagnin and A. Torcinovich"

import NeuralNetwork

import mnist_loader
import numpy as np


np.random.seed(314)

print("Loading data")
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()

print("Generating desired CNN")
# vec = [784, ("cl", 5, 1, "sigmoid"), ("pl", 2, "mean"), ("fcl", 100, "sigmoid"), ("fcl", 10, "sigmoid")]
vec = [784, ("fcl", 100, "sigmoid"), ("fcl", 10, "sigmoid")]
net = NeuralNetwork.NeuralNetwork(vec, "quadratic")

print("Training CNN")
net.training(list(training_data), 30, 10, 3.0)

print("Testing CNN performances")
net.testing(list(test_data))
