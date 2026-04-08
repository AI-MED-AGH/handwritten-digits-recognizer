import torchvision
from fastmlapi import MLController, preprocessing, postprocessing, prediction
import numpy as np
from scipy.ndimage import center_of_mass, shift
from pydantic import BaseModel, field_validator

from models.Model import MyModel
import torch

transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])


class RequestModel(BaseModel):
    data: list[list[int]]

    @field_validator("data")
    @classmethod
    def validate_data(cls, raw_data: list[list[int]]) -> np.ndarray:
        data = np.array(raw_data, dtype=int)
        assert data.min() >= 0, "data must be between 0-255"
        assert data.max() <= 255, "data must be between 0-255"
        assert data.ndim == 2, "Expected list of cases, each case being 784 int array"
        assert data.shape[1] == (
                    28 * 28), f"Images should be provided as a flat array of length 784, but length was {data.shape[1]}"
        return data


class ClassifierServer(MLController):
    model_name = "handwritten-digits-recognizer"
    model_version = "1.0.0"

    request_model = RequestModel

    def load_model(self) -> MyModel:
        PATH = "trained_models/model_fine_tuned.pth"
        model = MyModel()
        model.load_state_dict(torch.load(PATH, weights_only=True))
        return model

    @preprocessing
    def preprocess(self, data) -> torch.Tensor:
        from scipy.ndimage import center_of_mass, shift
        X = np.array(data, dtype=np.float32) / 255.0
        X = X.reshape((-1, 28, 28))

        # Image centering based on its center of mass
        processed_images = []
        for image in X:
            # Calculate image's center of mass
            c_y, c_x = center_of_mass(image)

            # If canvas is completely black, None will be assigned to c_x or c_y
            if np.isnan(c_x) or np.isnan(c_y):
                processed_images.append(image)
                continue

            # Calculate the shift vector
            shift_x = 13.5 - c_x
            shift_y = 13.5 - c_y

            shifted_image = shift(image, shift=(shift_y, shift_x), cval=0.0)

            processed_images.append(shifted_image)

        # Reshape centered image
        X_centered = np.array(processed_images).reshape((-1, 1, 28, 28))

        X_tensor = torch.from_numpy(X_centered)
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
