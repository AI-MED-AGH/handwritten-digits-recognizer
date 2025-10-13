import time

import torchvision

import matplotlib.pyplot as plt
import numpy as np
import torch

import traceback
import os
from Model import MyModel

PATH = "trained_models/model.pth"


tranform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])

model = MyModel()

model.load_state_dict(torch.load(PATH, weights_only=True))


INPUT_PIPE_NAME = "model_input.pipe"
OUTPUT_PIPE_NAME = "model_output.pipe"

if not os.path.exists(INPUT_PIPE_NAME):
    os.mkfifo(INPUT_PIPE_NAME)

if not os.path.exists(OUTPUT_PIPE_NAME):
    os.mkfifo(OUTPUT_PIPE_NAME)


print("==================================")
print("   Model loaded, listening...")
print("=================================\n")


while True:
    with open(INPUT_PIPE_NAME, 'r') as input_file:
        pred_start_time = time.time()

        input_data = input_file.read().rstrip('\n')
        input_data = input_data.split(',')

        # print("Strings array: ", input_data)

        try:
            X = np.array(input_data, dtype=np.float32) / 255.0
            X = X.reshape((28,28))
        except ValueError:
            # Wrong size or something...
            traceback.print_exc()
            continue
        
        # print(f"Received: {X.shape} {X}")

        with torch.no_grad():
            x_tensor = torch.unsqueeze(tranform(X),0)

            # print(f"{x_tensor=}")
            output=model(x_tensor)

            model.eval()
            predictions: np.ndarray = np.exp(output.numpy())
            
        predicted_labels = np.argmax(predictions, axis=1)

        # print(output)
        print(predictions)

        pred_end_time = time.time()
        print(f"Prediction duration: {pred_end_time - pred_start_time}")

        predictions: list[str] = (predictions * 255).flatten().astype(int).astype(str).tolist()
        predictions = ",".join(predictions)

        with open(OUTPUT_PIPE_NAME, "w") as output_file:
            output_file.write(predictions)
            output_file.flush()

            plt.imshow(X.reshape(28, 28), cmap='gray')
            plt.title(f"Predicted: {predicted_labels}")
            plt.axis('off')
            plt.savefig("debug_inputs/last.png")
