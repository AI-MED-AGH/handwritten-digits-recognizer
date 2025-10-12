import time

start_time = time.time()


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tensorflow.keras.layers import Dense, Flatten, Input
from tensorflow.keras.models import Sequential

import traceback
import os

model = Sequential([
    Input(shape=(28, 28, 1)),  # This defines the input shape correctly
    Flatten(),
    Dense(128, activation='relu'),
    Dense(64, activation='relu'),
    Dense(10, activation='softmax')
])
# model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])


model.load_weights('model.weights.h5')

mid_time = time.time()

INPUT_PIPE_NAME = "model_input.pipe"
OUTPUT_PIPE_NAME = "model_output.pipe"

if not os.path.exists(INPUT_PIPE_NAME):
    os.mkfifo(INPUT_PIPE_NAME)

if not os.path.exists(OUTPUT_PIPE_NAME):
    os.mkfifo(INPUT_PIPE_NAME)


print("Model loaded, listening...")


while True:
    with open(INPUT_PIPE_NAME, 'r') as input_file:
        pred_start_time = time.time()

        input_data = input_file.read().rstrip('\n')
        input_data = input_data.split(',')

        print("Strings array: ", input_data)

        try:
            X = np.array(input_data, dtype=float) / 255.0
            X = X.reshape(-1, 28, 28, 1)
        except ValueError:
            # Wrong size or something...
            traceback.print_exc()
            continue

        print(f"Received: {X.shape} {X}")
        predictions: np.ndarray = model.predict(X)
        predicted_labels = np.argmax(predictions, axis=1)

        pred_end_time = time.time()
        print(f"Prediction duration: {pred_end_time - pred_start_time}")

        predictions: list[str] = (predictions * 255).flatten().astype(int).astype(str).tolist()
        predictions = ",".join(predictions)

        with open(OUTPUT_PIPE_NAME, "w") as output_file:
            output_file.write(predictions)
            output_file.flush()

            # plt.imshow(X.reshape(28, 28), cmap='gray')
            # plt.title(f"Predicted: {predicted_labels}")
            # plt.axis('off')
            # plt.show()


end_time = time.time()

print(f"Duration: {end_time - start_time} seconds")
print(f"Model loading: {mid_time - start_time} seconds")
