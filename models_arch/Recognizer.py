import torch
import torch.nn as nn
import numpy as np
from pathlib import Path


class BaseRecognizer(nn.Sequential):
    def __init__(self, *args, save_path: Path|str = None):
        super().__init__(*args)
        if isinstance(save_path, str):
            save_path = Path(save_path)
        if not isinstance(save_path, Path):
            raise ValueError(f'This is not a path: {path}')
        
        self.save_path: Path = save_path

    @property
    @torch.no_grad
    def kernels(self) -> np.ndarray:
        """Collect all kernels of conv layers of the model and put them in a np.ndarray

        Returns:
            np.ndarray: Array containing all kernels
        """
        kers = []
        self.eval()
        for layer in self:
            if isinstance(layer, nn.Conv2d):
                for k in layer.weight:
                    kers.append(k)

        return np.array(kers, dtype=float)

    def save(self, path: Path|str = None):
        if path is None:
            path = self.save_path

        torch.save(self.state_dict(), path)

    def load(self, path: Path|str = None):
        if path is None:
            path

        self.load_state_dict(torch.load(self.save_path, weights_only=True))


class RecognizerV1(BaseRecognizer):
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

            nn.LogSoftmax(),

            save_path='trained_models/RecognizerV1.pth'
        )

class RecognizerV2(BaseRecognizer):
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
            nn.BatchNorm2d(20),
            nn.ReLU(),
            
            # Flatten data in order to feed it to linear layers
            nn.Flatten(), # shape : 20 x 7 x 7

            # 1st linear layer
            nn.Linear(in_features=980, out_features=128), 
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

            save_path='trained_models/RecognizerV2.pth'
        )

class RecognizerV3ker3(BaseRecognizer):
    def __init__(self):
        super().__init__(
            # 1st convolution
            nn.Conv2d(in_channels=1, out_channels=8, kernel_size=3, padding=1),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # shape : 8 x 14 x 14 
            
            # 2nd convolution
            nn.Conv2d(in_channels=8, out_channels=16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # shape : 16 x 7 x 7 
            nn.Dropout(p=0.3),

            # Flatten data in order to feed it to linear layers
            nn.Flatten(), # shape : 784

            # 1st linear layer
            nn.Linear(in_features=784, out_features=64), 
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(p=0.5),

            # output layer with one shadow class
            nn.Linear(in_features=64, out_features=11),

            save_path='trained_models/RecognizerV3ker3.pth'
        )

class RecognizerV3ker5(BaseRecognizer):
    def __init__(self):
        super().__init__(
            # 1st convolution
            nn.Conv2d(in_channels=1, out_channels=8, kernel_size=5, padding=2),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # shape : 8 x 14 x 14 
            
            # 2nd convolution
            nn.Conv2d(in_channels=8, out_channels=16, kernel_size=5, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # shape : 16 x 7 x 7 
            nn.Dropout(p=0.3),

            # Flatten data in order to feed it to linear layers
            nn.Flatten(), # shape : 784

            # 1st linear layer
            nn.Linear(in_features=784, out_features=64), 
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(p=0.5),

            # output layer with one shadow class
            nn.Linear(in_features=64, out_features=11),

            save_path='trained_models/RecognizerV3ker5.pth'
        )

class RecognizerOneConv(BaseRecognizer):
    def __init__(self):
        super().__init__(
            # 1st convolution
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=5, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # shape : 16 x 14 x 14
            nn.Dropout2d(p=0.3),

            # Flatten data in order to feed it to linear layers
            nn.Flatten(), # shape : 1568

            # 1st linear layer
            nn.Linear(in_features=3136, out_features=64), 
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(p=0.3),

            # output layer with one shadow class
            nn.Linear(in_features=64, out_features=11),

            save_path='trained_models/RecognizerOneConv.pth'
        )