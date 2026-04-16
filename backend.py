import torch
import torch.nn.functional as F
import numpy as np
from scipy.ndimage import center_of_mass, shift
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
import os, csv

# Initialize the FastAPI application
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the model architecture from the external file
from models_arch.recognizer import *

# Load the model
model = RecognizerV3ker5()  # Change recognizer if you have used different recognizer while model training
MODEL_PATH = "trained_models/model_fine_tuned.pth"  # Change model path

try:
    # Load weights into the model
    state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()
    print("Model loaded successfully!")
except FileNotFoundError:
    print(f"ERROR: Model weights file not found at: {MODEL_PATH}")


# Input validation schema
class RequestModel(BaseModel):
    data: list[list[int]]

    @field_validator("data")
    @classmethod
    def validate_data(cls, raw_data: list[list[int]]) -> list[list[int]]:
        data_np = np.array(raw_data, dtype=int)
        assert data_np.min() >= 0, "Pixel values must be between 0 and 255"
        assert data_np.max() <= 255, "Pixel values must be between 0 and 255"
        assert data_np.ndim == 2, "Expected a list of images, each being a 784-element array"
        assert data_np.shape[1] == (28 * 28), f"Images should have length 784, but got {data_np.shape[1]}"
        return raw_data


# Prediction endpoint
@app.post("/predict")
async def predict(request: RequestModel):
    # --- PREPROCESSING ---
    # Convert to float tensor scaled to 0.0 - 1.0
    X = np.array(request.data, dtype=np.float32) / 255.0
    X = X.reshape((-1, 28, 28))

    processed_images = []
    for image in X:
        # Calculate the center of mass
        c_y, c_x = center_of_mass(image)

        # Handle completely empty (black) images
        if np.isnan(c_x) or np.isnan(c_y):
            processed_images.append(image)
            continue

        # Calculate shift vector to center the image at (13.5, 13.5)
        shift_x = 13.5 - c_x
        shift_y = 13.5 - c_y

        # Apply the shift
        shifted_image = shift(image, shift=(shift_y, shift_x), cval=0.0)
        processed_images.append(shifted_image)

    # Format input for the network (Batch Size, Channels, Height, Width)
    X_centered = np.array(processed_images).reshape((-1, 1, 28, 28))
    X_tensor = torch.from_numpy(X_centered)

    # --- PREDICTION ---
    with torch.no_grad():
        output = model(X_tensor)

    # --- POSTPROCESSING ---
    # Convert logits to probabilities (0.0 - 1.0) using Softmax
    probabilities = F.softmax(output, dim=1).numpy()
    predicted_labels = np.argmax(probabilities, axis=1)

    # Construct the response
    response = [
        {
            "label": int(label),
            "proba": proba.tolist(),
        }
        for label, proba in zip(predicted_labels, probabilities)
    ]

    return response


# Path to the fine-tuning data
DATA_FOLDER = "fine-tuning-data-collector"
CSV_FILE = os.path.join(DATA_FOLDER, "fine_tune_data.csv")

# Create folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


class CollectionModel(BaseModel):
    label: int
    pixels: list[int]


@app.post("/collect")
async def collect_data(item: CollectionModel):
    # Prepare header if file is new
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        # Optional: add header on first run
        if not file_exists:
            header = ["label"] + [f"pixel_{i}" for i in range(784)]
            writer.writerow(header)

        # Write label followed by flattened pixel list
        writer.writerow([item.label] + item.pixels)

    return {"status": "success", "message": f"Data for digit {item.label} saved."}

app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)