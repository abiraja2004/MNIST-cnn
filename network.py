import numpy as np

import functions as f
import layers as l
import utils as u


class NeuralNetwork():
    def __init__(self, layers, cost_func):
        """
        Initialize the data. Initial weights and biases are chosen randomly from a gaussian distribution

        :param layers: a vector which stores each layer of the network
        :param cost_func: the cost function applied to the network
        """
        assert len(layers) > 0
        self.input_layer = layers[0]
        self.output_layer = layers[-1]
        self.layers = [(prev_layer, layer) for prev_layer, layer in zip(layers[:-1], layers[1:])]

        self.cost_func = cost_func
        self.der_cost_func = f.get_derivative(cost_func)

        self.input_weights = {}
        self.input_biases = {}
        for prev_layer, layer in self.layers:
            layer.connect_to(prev_layer)

            prev_layer_num_neurons_out = prev_layer.depth * prev_layer.height * prev_layer.width
            layer_num_neurons_out      = layer.depth      * layer.height      * layer.width
            if type(layer) is l.FullyConnectedLayer:
                self.input_weights[layer] = u.glorot_uniform((layer_num_neurons_out, prev_layer_num_neurons_out),
                                                             prev_layer_num_neurons_out, layer_num_neurons_out)
                self.input_biases[layer] =  np.zeros((layer_num_neurons_out, 1))
            elif type(layer) is l.ConvolutionalLayer:
                self.input_weights[layer] = u.glorot_uniform((layer.depth, prev_layer.depth, layer.kernel_size, layer.kernel_size),
                                                             prev_layer_num_neurons_out, layer_num_neurons_out)
                self.input_biases[layer] =  np.zeros((layer.depth, 1))
            elif type(layer) is l.PollingLayer:
                if not isinstance(prev_layer, l.ConvolutionalLayer):
                    raise NotImplementedError
                self.input_weights[layer] = np.array([])
                self.input_biases[layer] =  np.array([])
            else:
                raise NotImplementedError

    def __str__(self):
        s = "NeuralNetwork([\n"
        for prev_layer, layer in self.layers:
            s += "    %s,\n" % prev_layer
        s += "    %s\n" % self.output_layer
        s += "], cost_func=%s)" % self.cost_func.__name__
        return s

    def feedforward(self, x):
        """
        Perform the feedforward of one observation and return the list of z and activations of each layer

        :param x: the observation taken as input layer
        """
        # the input layer hasn't zetas and its initial values are considered directly as activations
        self.input_layer.z = np.zeros_like(x)
        self.input_layer.a = x

        # feedforward the input for each layer
        for prev_layer, layer in self.layers:
            input_w = self.input_weights[layer]
            input_b = self.input_biases[layer]
            layer.feedforward(prev_layer, input_w, input_b)

    def backpropagate(self, batch, eta):
        """
        Perform the backpropagation for one observation and return the derivative of the weights relative to each layer

        :param batch: the batch used to train the network
        :param eta: the learning rate
        """
        # store the sum of derivatives of the input weights and biases of each layer, computed during batch processing
        batch_der_weights = {layer: np.zeros_like(self.input_weights[layer]) for prev_layer, layer in self.layers}
        batch_der_biases = {layer: np.zeros_like(self.input_biases[layer]) for prev_layer, layer in self.layers}

        # for each observation in the current batch
        for x, y in batch:
            # feedforward the observation
            self.feedforward(x)

            # backpropagate the error
            delta_z = self.der_cost_func(self.output_layer.a, y) * self.output_layer.der_act_func(self.output_layer.z)
            for prev_layer, layer in reversed(self.layers):
                input_w = self.input_weights[layer]
                der_input_w, der_input_b, delta_z = layer.backpropagate(prev_layer, input_w, delta_z)
                batch_der_weights[layer] += der_input_w
                batch_der_biases[layer] += der_input_b

        # update weights and biases with the results of the current batch
        for prev_layer, layer in self.layers:
            self.input_weights[layer] -= eta / len(batch) * batch_der_weights[layer]
            self.input_biases[layer] -= eta / len(batch) * batch_der_biases[layer]


def train(net, inputs, num_epochs, batch_size, eta):
    """
    Train the network according to the Stochastic Gradient Descent (SGD) algorithm

    :param net: the network to train
    :param inputs: the observations that are going to be used to train the network
    :param num_epochs: the number of epochs
    :param batch_size: the size of the batch used in single cycle of the SGD
    :param eta: the learning rate
    """
    assert eta > 0

    for i in range(num_epochs):
        np.random.shuffle(inputs)

        # divide input observations into batches of size batch_size
        batches = [inputs[j:j + batch_size] for j in range(0, len(inputs), batch_size)]
        for j, batch in enumerate(batches):
            u.print("Epoch %d [%d/%d]" % (i+1, j+1, len(batches)), override=True)
            net.backpropagate(batch, eta)

def test(net, tests):
    """
    Test the network and return some performances index. Note that the classes must start from 0

    :param tests: the observations that are going to be used to test the performances of the network
    """
    perf = 0
    for x, y in tests:
        net.feedforward(x)
        res = net.layers[-1][1].a
        if np.argmax(res) == np.argmax(y): perf += 1

    print("{} correctly classified observations ({}%)".format(perf, 100 * perf / len(tests)))
