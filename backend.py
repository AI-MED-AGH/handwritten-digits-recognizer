import torch
import torch.nn as nn
import torch.nn.functional as F
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 1. ARCHITEKTURA ODTWORZONA NA PODSTAWIE TWOICH BŁĘDÓW
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # Checkpoint mówi: conv1 ma 10 filtrów 5x5
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        # Checkpoint mówi: conv2 ma 20 filtrów 5x5, wchodzących 10
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        # Checkpoint mówi: fc1 ma 320 wejść i 50 wyjść
        self.fc1 = nn.Linear(320, 50)
        # Checkpoint mówi: fc2 ma 50 wejść i 10 wyjść
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2(x), 2))
        x = x.view(-1, 320) # Spłaszczenie do fc1
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ŁADOWANIE MODELU
model = Net()
# Upewnij się, że nazwa pliku to dokładnie ta, którą masz na dysku!
MODEL_PATH = "model.pth"

try:
    state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
    model.load_state_dict(state_dict)
    model.eval()
    print("Model załadowany pomyślnie!")
except FileNotFoundError:
    print(f"BŁĄD: Nie znaleziono pliku {MODEL_PATH} w folderze serwera.")

class DigitInput(BaseModel):
    tensor: list[float]

@app.post("/predict")
async def predict(data: DigitInput):
    # Model oczekuje formatu (B, C, H, W) -> (1, 1, 28, 28)
    input_tensor = torch.tensor(data.tensor, dtype=torch.float32).view(1, 1, 28, 28)
    
    with torch.no_grad():
        output = model(input_tensor)
        # Zamiana na prawdopodobieństwa (0-1)
        probabilities = F.softmax(output, dim=1)[0].tolist()
        
    return {"weights": probabilities}

app.mount("/ui", StaticFiles(directory="."), name="ui")

@app.get("/")
async def read_index():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)