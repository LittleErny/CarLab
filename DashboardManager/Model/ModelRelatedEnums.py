from enum import Enum


# Enum for categorical options
class LossFunctions(Enum):  # For gradient boosting models
    SQUARED_ERROR = "squared_error"
    ABSOLUTE_ERROR = "absolute_error"


class NeuralNetworkActivations(Enum):  # For neural networks
    RELU = "relu"
    TANH = "tanh"
    SIGMOID = "sigmoid"


class NeuralNetworkOptimizers(Enum):  # For neural networks
    SGD = "sgd"
    ADAM = "adam"
    RMSPROP = "rmsprop"


class NeuralNetworkLossFunctions(Enum):  # For neural networks
    MSE = "mean_squared_error"
    MAE = "mean_absolute_error"
    HUBER = "huber_loss"
