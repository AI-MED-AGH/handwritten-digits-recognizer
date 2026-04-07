from torch import nn, Tensor
import torch.nn.functional as func

class RecognizerV1(nn.Sequential):
    def __init__(self):
        super().__init__(
            # 1st convolution
            nn.Conv2d(in_channels=1, out_channels=10, kernel_size=5, padding=2),
            nn.ReLU(),
            
            # 2nd convolution
            nn.Conv2d(in_channels=10, out_channels=20, kernel_size=5, padding=2),
            nn.ReLU(),
            
            # 3rd convolution withc maxPooling
            nn.Conv2d(in_channels=20, out_channels=20, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            
            # Flatten data in order to feed it to linear layers
            nn.Flatten(),

            # 1st linear layer
            nn.Linear(in_features=3920, out_features=128), 
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(p=0.6),

            # 2nd linera layer
            nn.Linear(in_features=128, out_features=32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(p=0.6),

            # output layer with one shadow class
            nn.Linear(in_features=32, out_features=11),

            nn.LogSoftmax()
        )

class RecognizerV2(nn.Sequential):
    def __init__(self, *args):
        super().__init__(
            # 1st convolution
            nn.Conv2d(in_channels=1, out_channels=10, kernel_size=5, padding=2),
            nn.BatchNorm2d(10),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # shape : 10 x 14 x 14 
            
            # 2nd convolution
            nn.Conv2d(in_channels=10, out_channels=20, kernel_size=5, padding=2),
            nn.BatchNorm2d(20),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # shape : 20 x 7 x 7 

            # 3rd convolution
            nn.Conv2d(in_channels=20, out_channels=20, kernel_size=5, padding=2),
            nn.BatchNorm2d(),
            nn.ReLU(),
            
            # Flatten data in order to feed it to linear layers
            nn.Flatten(), # shape : 20 x 7 x 7

            # 1st linear layer
            nn.Linear(in_features=280, out_features=128), 
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(p=0.5),

            # 2nd linear layer
            nn.Linear(in_features=128, out_features=32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(p=0.3),

            # output layer with one shadow class
            nn.Linear(in_features=32, out_features=11),
        )