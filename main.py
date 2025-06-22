import torch
from perception import SimplePerceptionNet, perfect_perception
from vehicle import Vehicle
from controller import Controller
from controllerLTSLogger import ControllerLTSLogger
from vehicleLTSLogger import VehicleLTSLogger

import time

def run_simulation():
    USE_PERFECT_PERCEPTION = True

    # Load model only if needed
    if not USE_PERFECT_PERCEPTION:
        model = SimplePerceptionNet()
        model.eval()

    # Perception function depending on config
    def get_perception_output(obstacle_distance):
        if USE_PERFECT_PERCEPTION:
            return perfect_perception(obstacle_distance)
        else:
            dummy_input = torch.randn(1, 3, 28, 28)
            output = model(dummy_input)
            return output.argmax(dim=1).item()

    # Create vehicle instance
    vehicle = Vehicle()

    # Initialise loggers
    controller_logger = ControllerLTSLogger()
    vehicle_logger = VehicleLTSLogger(vehicle)

    # Create controller with logger
    controller = Controller(vehicle, controller_logger)

    # Run simulation
    for step in range(15):
        # Obstacle distance simulation
        obstacle_distance = max(0, 15 - step * 1.0)
        perception_output = get_perception_output(obstacle_distance)

        # Get control commands
        steering, acceleration = controller.control(perception_output, obstacle_distance)

        # Log controller decision
        controller_logger.log(perception_output, obstacle_distance, controller.state)

        # Step vehicle and log transition
        vehicle_logger.step_and_log(steering, acceleration)

        # Print simulation step
        print(f"Step {step} -  State {controller.state}, Pos=({vehicle.x:.2f}, {vehicle.y:.2f}), Vel={vehicle.v:.2f}, "
              f"Perception={'Obstacle' if perception_output==1 else 'Clear'}, "
              f"ObstacleDist={obstacle_distance:.2f}, Acc={acceleration:.2f}")

        time.sleep(0.1)

    # Print LTS traces
    controller_logger.print_lts()
    vehicle_logger.print_lts()

if __name__ == "__main__":
    run_simulation()
