import torch
from perception import SimplePerceptionNet, perfect_perception
from vehicle import Vehicle
from controller import Controller
from controllerLTSLogger import ControllerLTSLogger
from vehicleLTSLogger import VehicleLTSLogger
from loggerUtils import colour_line_by_state
from visualiseLTS import visualise_lts

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

    for step in range(17):
        obstacle_distance = max(0, 15 - step * 1.0)
        perception_output = get_perception_output(obstacle_distance)

        steering, acceleration = controller.control(perception_output, obstacle_distance)

        dt = 0.1
        vehicle.v += acceleration * dt
        if vehicle.v <= 1e-5:
            vehicle.v = 0.0
            acceleration = 0.0
            vehicle.stopped = True

        controller_logger.log(perception_output, obstacle_distance, controller.state)

        vehicle_logger.step_and_log(steering, acceleration, perception_output, controller.state)

        line = (
            f"Step {step} -  State {controller.state}, "
            f"Pos=({vehicle.x:.2f}, {vehicle.y:.2f}), "
            f"Vel={vehicle.v:.2f}, "
            f"Perception={'Obstacle' if perception_output == 1 else 'Clear'}, "
            f"ObstacleDist={obstacle_distance:.2f}, "
            f"Acc={acceleration:.2f}"
        )

        print(colour_line_by_state(line, controller.state))
        time.sleep(0.1)

    # Print LTS traces
    controller_logger.print_lts()
    vehicle_logger.print_lts()

    visualise_lts(controller_logger.get_transitions())
    visualise_lts(vehicle_logger.get_transitions())

if __name__ == "__main__":
    run_simulation()
