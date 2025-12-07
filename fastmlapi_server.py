from fastmlapi import MLController, preprocessing, postprocessing
import numpy as np

from Model import MyModel
import os.path
import torch


class ClassifierServer(MLController):
    model_name = "handwritten-digits-recognizer"
    model_version = "1.0.0"

    def load_model(self):
        PARAMS_PATH = os.path.join("trained_models", "model.pth")
        model = MyModel()
        model.load_state_dict(torch.load(PARAMS_PATH))
        return model

    @preprocessing
    def preprocess(self, data) -> torch.Tensor:
        data = np.array(data).reshape((len(data), 1, 28, 28)) / 255.0
        data = torch.Tensor(data)
        return data

    @postprocessing
    def postprocess(self, prediction: np.ndarray) -> list:
        pred = prediction.data.max(1, keepdim=True)[1]
        return pred.tolist()

if __name__ == "__main__":
    ClassifierServer().run()
