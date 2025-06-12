import torch
import torch.nn as nn
import torch.nn.functional as F

class SimplePerceptionNet(nn.Module):
    def __init__(self):
        super().__init__()
        # First convolutional layer:
        # Input channels = 3 (RGB image), output channels = 8, kernel size = 3x3
        self.conv1 = nn.Conv2d(3, 8, 3)
        # Max pooling layer with 2x2 kernel to downsample feature maps
        self.pool = nn.MaxPool2d(2)
        # Second convolutional layer:
        # Input channels = 8, output channels = 16, kernel size = 3x3
        self.conv2 = nn.Conv2d(8, 16, 3)
        # Fully connected layer:
        # Input features = 16 channels * 5 height * 5 width = 400,
        # output features = 32
        self.fc1 = nn.Linear(16 * 5 * 5, 32)
        # Final fully connected layer mapping to 2 output classes
        self.fc2 = nn.Linear(32, 2)
    
    def forward(self, x):
        # Pass input through conv1, apply ReLU activation and pool
        x = self.pool(F.relu(self.conv1(x)))
        # Pass result through conv2, apply ReLU activation and pool
        x = self.pool(F.relu(self.conv2(x)))
        # Flatten the 3D tensor to 1D (batch_size x features)
        x = torch.flatten(x, 1)
        # Apply first fully connected layer with ReLU
        x = F.relu(self.fc1(x))
        # Final fully connected layer (outputs raw scores for each class)
        x = self.fc2(x)
        return x
