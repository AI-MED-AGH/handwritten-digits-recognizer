import os
import traceback

import numpy as np

INPUT_PIPE_NAME = "model_input.pipe"
OUTPUT_PIPE_NAME = "model_output.pipe"

if not os.path.exists(INPUT_PIPE_NAME):
    os.mkfifo(INPUT_PIPE_NAME)

if not os.path.exists(OUTPUT_PIPE_NAME):
    os.mkfifo(INPUT_PIPE_NAME)


while True:
    with open(INPUT_PIPE_NAME, 'r') as fifo:
        input_data = fifo.read().rstrip('\n')
        input_data = input_data.split(',')

        try:
            X = np.array(input_data, dtype=float) / 255.0
            X = X.reshape(-1, 28, 28, 1)
        except ValueError:
            # Wrong size or something...
            traceback.print_exc()
            continue

        print(f"Received: {X.shape} {X}")
