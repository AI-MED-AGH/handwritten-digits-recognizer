import torchvision
from fastmlapi import MLController, preprocessing, postprocessing, prediction
import numpy as np

from Model import MyModel
import torch

transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])


class ClassifierServer(MLController):
    model_name = "handwritten-digits-recognizer"
    model_version = "1.0.0"

    def load_model(self) -> MyModel:
        PATH = "trained_models/model.pth"
        model = MyModel()
        model.load_state_dict(torch.load(PATH, weights_only=True))
        return model

    @preprocessing
    def preprocess(self, data: list[list[int]]) -> torch.Tensor:
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
    def postprocess(self, probabilities: torch.Tensor) -> list:
        probabilities: np.ndarray = np.exp(probabilities.numpy())
        predicted_labels = np.argmax(probabilities, axis=1)

        response = [
            {
                "label": label.tolist(),
                "proba": proba.tolist(),
            }
            for label, proba in zip(predicted_labels, probabilities)
        ]

        return response

if __name__ == "__main__":
    ClassifierServer().run()
