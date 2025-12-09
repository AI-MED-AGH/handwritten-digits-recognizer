import torchvision
from fastmlapi import MLController, preprocessing, postprocessing, prediction
import numpy as np
from pydantic import BaseModel, field_validator

from Model import MyModel
import torch

transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])


class RequestModel(BaseModel):
    data: list[list[int]]

    @classmethod
    @field_validator("data")
    def validate_data(cls, raw_data: list[list[int]]) -> np.ndarray:
        data = np.array(raw_data)

        print("validating data... ", data.shape)

        assert data.dtype == np.int32, "data must be an integer"
        assert data.min() >= 0, "data must be between 0-255"
        assert data.max() <= 255, "data must be between 0-255"
        assert data.ndim == 2, "Expected list of cases, each case being 784 int array"
        assert data.shape[2] == (28 * 28), "Images should be 28x28 px, provided as a flat array (784 long)"

        return data


class ClassifierServer(MLController):
    model_name = "handwritten-digits-recognizer"
    model_version = "1.0.0"

    request_model = RequestModel

    def load_model(self):
        self.request_model = RequestModel
        PATH = "trained_models/model.pth"
        model = MyModel()
        model.load_state_dict(torch.load(PATH, weights_only=True))
        return model

    @preprocessing
    def preprocess(self, data) -> torch.Tensor:
        X = np.array(data, dtype=np.float32) / 255.0
        X = X.reshape((-1, 1, 28, 28))
        X_tensor = torch.from_numpy(X)
        return X_tensor

    @prediction
    def prediction(self, X: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            self.model.eval()
            output = self.model(X)
            return output

    @postprocessing
    def postprocess(self, probabilities) -> list:
        probabilities: np.ndarray = np.exp(probabilities.numpy())
        predicted_labels = np.argmax(probabilities, axis=1)

        response = [
            {
                "label": label.tolist(),
                "proba": proba.tolist()
            }
            for label, proba in zip(predicted_labels, probabilities)
        ]

        return response


if __name__ == "__main__":
    ClassifierServer().run()
