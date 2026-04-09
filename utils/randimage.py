from torchvision.transforms import Compose, ToTensor
from torchvision.utils import save_image
import torch
from numpy import random

class RandomImageGenerator:
    def __init__(self, img_size: tuple[int, int]|None = None) -> None:
        if img_size is None:
            img_size = (28, 28)
        self.size = img_size

    def __call__(self, *args, **kwds):
        raise NotImplementedError('This method should be overwritten')
    

class RandomLinesGenerator(RandomImageGenerator):
    def __init__(self, img_size: tuple[int, int]|None = None, max_lines: int = 3):
        super().__init__(img_size)
        self.max_lines = max_lines


    def generate(self, size: int = None, max_lines: int = None) -> torch.Tensor:
        """
        Generates a grayscale image tensor with random curved 'pencil-like' lines, using quadratic Bezier curves
        """
        if size is None:
            size = self.size
        
        if max_lines is None:
            max_lines = self.max_lines

        # 1. Create a 2D coordinate grid and expand dimensions for vectorization
        x = torch.arange(size[0], dtype=torch.float32)
        y = torch.arange(size[1], dtype=torch.float32)
        yy, xx = torch.meshgrid(y, x, indexing='ij')
        
        # Add a 3rd dimension to the grid so we can compute distances to many points at once
        xx = xx.unsqueeze(2) # Shape: (28, 28, 1)
        yy = yy.unsqueeze(2) # Shape: (28, 28, 1)

        # 2. Initialize a black background
        image = torch.zeros(size, dtype=torch.float32)

        # 3. Determine random number of lines
        num_lines = random.randint(0, max_lines + 1)

        for _ in range(num_lines):
            # Random control points for a Quadratic Bezier curve
            p0 = torch.tensor([random.uniform(0, size[0]), random.uniform(0, size[1])]) # Start
            p1 = torch.tensor([random.uniform(0, size[0]), random.uniform(0, size[1])]) # Control (pulls the curve)
            p2 = torch.tensor([random.uniform(0, size[0]), random.uniform(0, size[1])]) # End
 

            # 4. Generate 100 points along the curve using parameter t from 0 to 1
            t = torch.linspace(0, 1, steps=100).unsqueeze(1)    # Shape: (100, 1)
            curve = (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2  # Shape: (100, 2)

            # Extract X and Y coordinates of the curve and reshape to broadcast against the canvas
            cx = curve[:, 0].view(1, 1, -1) # Shape: (1, 1, 100)
            cy = curve[:, 1].view(1, 1, -1) # Shape: (1, 1, 100)

            # 5. Create grainy pencil texture 
            sigma = random.uniform(0.9, 1.1)   # spread of the line
            intensity = 1.0

            # 6. Draw the brush strokes for all 100 points simultaneously
            # This creates a 3D tensor of shape (28, 28, 100) containing 100 tiny dots
            strokes = intensity * torch.exp(-((xx - cx)**2 + (yy - cy)**2) / (2 * sigma**2))

            # 7. Merge the 100 dots into a single flat line
            # Using max() instead of sum() mimics a physical pencil sliding across paper,
            # preventing the overlapping areas from glowing unnaturally bright.
            line_image, _ = torch.max(strokes, dim=2)

            # 8. Add the completed line to the main canvas
            image += line_image

        # Clamp values to [0.0, 1.0] to prevent overlapping lines from exceeding white
        image = torch.clamp(image, 0.0, 1.0)

        return image

    def __call__(self, size: int = None, max_lines: int = None) -> torch.Tensor:
        return self.generate(size, max_lines)