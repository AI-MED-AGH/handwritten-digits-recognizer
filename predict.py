import torchvision
from fastmlapi import MLController, postprocessing, prediction
import numpy as np

from Model import MyModel
import torch

transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])


class ClassifierServer(MLController):
    model_name = "handwritten-digits-recognizer"
    model_version = "1.0.0"

    def load_model(self):
        PATH = "trained_models/model.pth"
        model = MyModel()
        model.load_state_dict(torch.load(PATH, weights_only=True))
        return model

    @prediction
    def preprocess_and_predict(self, data: torch.Tensor) -> torch.Tensor:
        X = np.array(data, dtype=np.float32) / 255.0
        X = X.reshape((-1, 1, 28, 28))

        X_tensor = torch.from_numpy(X)

        with torch.no_grad():
            self.model.eval()
            output = self.model(X_tensor)
            return output

    @postprocessing
    def postprocess(self, predictions) -> list:
        predictions: np.ndarray = np.squeeze(np.exp(predictions.numpy()))
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
