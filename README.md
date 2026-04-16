# Handwritten Digit Recognizer using CNN

This repository implements a Convolutional Neural Network (CNN) 
for recognizing handwritten digits from the MNIST dataset using 
PyTorch. The project also includes an interactive UI built with 
the Godot engine that allows users to draw digits and see
real-time predictions performed by the CNN model 
running in the background.

## Trained model (TODO)

Model weights (in .pth format) are excluded from this repository,
and instead can be downloaded from [huggingface](https://huggingface.co/K0D1Z/handwritten-digit-recognizer-agh-open-days/tree/main), and placed in the `trained_models` folder.

## CNN Model Architecture (TODO)

The CNN is a simple architecture with the following layers:

- Conv2d layer with 10 filters (kernel size 5) + ReLU + MaxPooling
- Conv2d layer with 20 filters + Dropout2d + ReLU + MaxPooling
- Fully connected layer with 50 units + ReLU
- Dropout + Output fully connected layer with 10 units (one per digit) + LogSoftmax


## Data and Training (TODO)

- Dataset: MNIST handwritten digits, automatically downloaded and loaded using torchvision.
- Training batch size: 64
- Testing batch size: 1000
- Optimizer: Adam
- Loss function: Negative Log Likelihood Loss (NLLLoss)
- Training epochs: 3
- Training loss and test accuracy are plotted during training (example accuracy on test set: ~97%).


## Setup and Installation
### Standard setup
1. Clone the repository
2. Create a virtual environment and install the dependencies:
    ```sh
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3. (Optional) change model path and model architecture in `backend.py`, `model_training.ipynb` and `fine_tuning.ipynb` 
4. Train the model (optional if you want to retrain):
   - Run `model_training.ipynb` in Jupyter to train and save the model to `trained_models/*` (by default `trained_models/RecognizerV3ker5.pth`).
   - OR download model from [huggingface](https://huggingface.co/K0D1Z/handwritten-digit-recognizer-agh-open-days/tree/main) to `trained_models` folder to `trained_models/`
5. Use fine-tuning data to retrain the model:
   - Copy fine-tuning CSV file into `fine-tuning-data-collector/fine_tune_data.csv`
   - Run `fine_tuning.ipynb` in Jupyter to train and save the model to `trained_models/model_fine_tuned.pth`
6. Run the backend app using uvicorn:
   ```sh
   uvicorn backend:app --reload --host 0.0.0.0 --port 8000
   ```
7. Run the HTTP server:
```sh
python -m http.server 3000
```
8. Paste `http://127.0.0.1:3000/` into your browser's URL bar

### Setup using Docker
1. Clone the repository 
2. Build and start the container:
```sh
docker-compose up --build
```
3. Open your browser and navigate to: http://localhost:8000