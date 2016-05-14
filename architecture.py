import json

import numpy as np

import theano
import theano.tensor as T

from layers.convpool import ConvPool
from layers.fc import FC
from layers.softmax import SoftMax

class Architecture(object):

    def __init__ (self, specs):
        self.specs = json.loads(specs)
        # Number of layers in DeepNet
        nl = len(self.specs) - 1

        # list would hold layers (ConvPool, FC, SoftMax etc.) 
        self.layer = [None] * nl
        
        # List holds the shape of output of a layer
        self.lout_shape = [None] * nl
        
        # INIT_FIRST_LAYER
        self.init_first_layer()
        
        # INIT_Subsequent_layer
        for i in range(1, nl):
            self.init_layer(i)


        self.cost = self.layer[nl-1].negative_log_likelihood(self.y)
        self.prob_y = self.layer[nl-1].prob_y
        self.pred_y = self.layer[nl-1].pred_y
        
        self.params = []
        for i in range(0, nl):
            self.params += self.layer[i].params

        self.batch_size = self.specs["meta"]["batch_size"]

    def init_first_layer(self):
        
        layer_type = self.specs["layer0"]["type"]
        input_shape = self.specs["layer0"]["input_shape"]
        if layer_type == "convpool":
            # Dimensions of X: (batch_size, channels, height, width)
            self.X = T.tensor4('Input_Image')
            self.y = T.ivector('Target_Class')
        
            n_filters = self.specs["layer0"]["n_filters"]
            poolsize = self.specs["layer0"]["poolsize"]
 
            self.layer[0] = ConvPool(self.X, 
                                    filter_shape = (n_filters,
                                                    input_shape[0],3,3),
                                    poolsize = poolsize)

            self.lout_shape[0] = (n_filters, (input_shape[1]-3+1)//2,
                                        (input_shape[2]-3+1)//2)
        elif layer_type == "fc":
            self.X = T.matrix('Input_Image')
            self.y = T.ivector('Target_Class')
            # For FC, input_shape should be of rasterized image
            units = self.specs["layer0"]["units"]
            self.layer[0] = FC(self.X, fan_in = np.prod(input_shape),
                                fan_out = units)
            self.lout_shape[0] = (units,)

            
        elif layer_type == "softmax":
            self.X = T.matrix('Input_Image')
            self.y = T.ivector('Target_Class')
            # For SoftMax, input_shape should be of rasterized image
            units = self.specs["layer0"]["units"]
            self.layer[0] = SoftMax(self.X, 
                                n_in = np.prod(input_shape),
                                n_out = units)
            self.lout_shape[0] = (units,)
        else:
            # TODO: Throw Exception
            print 'Invalid Layer Type'

        print self.lout_shape[0]

    def init_layer(self, index):
        
        json_index = "layer" + str(index)
        layer_type = self.specs[json_index]["type"]
        in_shape = self.lout_shape[index - 1]

        if layer_type == "convpool":
            n_filters = self.specs[json_index]["n_filters"]
            poolsize = self.specs[json_index]["poolsize"]
            
            self.layer[index] = ConvPool (self.layer[index - 1].output,
                                filter_shape =  (n_filters, in_shape[0], 3, 3),
                                poolsize =  poolsize)
            self.lout_shape[index] = (n_filters, (in_shape[1]-3+1)//2,
                                        (in_shape[2]-3+1)//2)
        
        elif layer_type == "fc":
            # If previous layer is ConvPool, need to flatter the input
            # Otherwise (in case of fc), we're good to go
            units = self.specs[json_index]["units"]
            self.layer[index] = FC(self.layer[index-1].output.flatten(2),
                                    fan_in = np.prod(in_shape), 
                                    fan_out = units)
            self.lout_shape[index] = (units,)
        
        elif layer_type == "softmax":
            units = self.specs[json_index]["units"]
            self.layer[index] = SoftMax(
                                self.layer[index-1].output.flatten(2),
                                n_in = np.prod(in_shape),
                                n_out = units)
            self.lout_shape[index] = (units,)
            
        print self.lout_shape[index]

if __name__ == '__main__':

    specs = '{"meta": {"input":"cifar", "batch_size":500}, ' + \
            '"layer0":{"type":"convpool","input_shape":[3,32,32], ' + \
            '"n_filters":30, "poolsize":[2,2]}, ' + \
            '"layer1":{"type":"fc", "units":500}, ' + \
            '"layer2":{"type":"softmax", "units": 10}}'
    net = Architecture(specs)

