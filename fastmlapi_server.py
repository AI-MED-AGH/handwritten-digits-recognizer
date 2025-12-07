import torchvision
from fastmlapi import MLController, preprocessing, postprocessing
import numpy as np

from Model import MyModel
import os.path
import torch

tranform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])


class ClassifierServer(MLController):
    model_name = "handwritten-digits-recognizer"
    model_version = "1.0.0"

    def load_model(self):
        PATH = "trained_models/model.pth"
        model = MyModel()
        model.load_state_dict(torch.load(PATH, weights_only=True))
        return model

    @preprocessing
    def preprocess(self, data) -> torch.Tensor:
        data = np.array(data).reshape((len(data), 1, 28, 28)) / 255.0
        data = torch.Tensor(data)
        return data

    @postprocessing
    def postprocess(self, predictions) -> list:
        predictions: np.ndarray = np.squeeze(np.exp(predictions.detach().numpy()))
        if len(predictions.shape) == 1:
            predictions = predictions.reshape(1, -1)

        predicted_labels = np.argmax(predictions, axis=1)

        response = [
            {
                "label": predicted_labels[i].tolist(),
                "proba": predictions[i].tolist()
            }
            for i in range(len(predicted_labels))
        ]

        return response

if __name__ == "__main__":
    ClassifierServer().run()
