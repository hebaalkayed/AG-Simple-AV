import torch
from perception import SimplePerceptionNet
from vehicle import Vehicle
from controller import Controller
import time

def run_simulation():
    # Initialize the perception model and set to evaluation mode (no training)
    model = SimplePerceptionNet()
    model.eval()

    # Initialize vehicle and controller
    vehicle = Vehicle()
    controller = Controller(vehicle)

    # Simulate for 50 timesteps (~5 seconds with dt=0.1s)
    for step in range(50):
        # Create a dummy image tensor of shape (batch=1, channels=3, height=28, width=28)
        dummy_input = torch.randn(1, 3, 28, 28)

        # Run perception model to get output scores for each class
        output = model(dummy_input)
        # Get predicted class: 0 (no obstacle) or 1 (obstacle)
        perception_output = output.argmax(dim=1).item()
        
        # Simulate obstacle distance reducing over time (approaching obstacle)
        obstacle_distance = max(0, 20 - step * 0.4)
        
        # Controller decides on steering and acceleration commands
        steering, acceleration = controller.control(perception_output, obstacle_distance)
        
        # Update vehicle state based on control commands
        vehicle.step(steering, acceleration)
        
        # Print simulation info
        print(f"Step {step}: Pos=({vehicle.x:.2f}, {vehicle.y:.2f}), Vel={vehicle.v:.2f}, "
              f"Perception={'Obstacle' if perception_output==1 else 'Clear'}, "
              f"ObstacleDist={obstacle_distance:.2f}, Acc={acceleration:.2f}")
        
        # Wait to simulate real-time (optional)
        time.sleep(0.1)

if __name__ == "__main__":
    run_simulation()
