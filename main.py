import torch
import time

from perception import SimplePerceptionNet, perfect_perception
from vehicle import Vehicle
from controller import Controller
from controllerLTSLogger import ControllerLTSLogger
from vehicleLTSLogger import VehicleLTSLogger
from loggerUtils import colour_line_by_state
from visualiseLTS import visualise_lts

def scenario_obstacle_approaches():
    return [max(0, 15 - step * 1.0) for step in range(17)]

def scenario_obstacle_appears_and_disappears():
    return [
        20, 20, 20, 20, 20,  # Steps 0–4: no obstacle
        5, 5, 5, 5, 5,       # Steps 5–9: obstacle present
        20, 20, 20, 20, 20, 20, 20  # Steps 10–16: no obstacle again
    ]

def scenario_obstacle_stays_and_disappears():
    return [
        20, 20, 20, # Steps 0–2: no obstacle
        5, 5,  # Steps 3-4: obstacle present
        3, 3, # Steps 5–6: obstacle close
        1, # Steps 7: obstacle very close
        9, 9, # Steps 8–9: obstacle present
        20, 20, 20, 20, 20, 20, 20  # Steps 10–16: no obstacle again
    ]
def run_case(obstacle_distances, case_name="Scenario"):
    print(f"\n--- Running {case_name} ---\n")

    USE_PERFECT_PERCEPTION = True
    if not USE_PERFECT_PERCEPTION:
        model = SimplePerceptionNet()
        model.eval()

    def get_perception_output(distance):
        if USE_PERFECT_PERCEPTION:
            return perfect_perception(distance)
        else:
            dummy_input = torch.randn(1, 3, 28, 28)
            output = model(dummy_input)
            return output.argmax(dim=1).item()

    vehicle = Vehicle()
    controller_logger = ControllerLTSLogger()
    vehicle_logger = VehicleLTSLogger(vehicle)
    controller = Controller(vehicle, controller_logger)

    dt = 0.1
    for step, obstacle_distance in enumerate(obstacle_distances):
        perception_output = get_perception_output(obstacle_distance)

        steering, acceleration = controller.control(perception_output, obstacle_distance)

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

    controller_logger.print_lts()
    vehicle_logger.print_lts()
    # visualise_lts(controller_logger.get_transitions())
    # visualise_lts(vehicle_logger.get_transitions())

def run_simulation():
    run_case(scenario_obstacle_approaches(), case_name="Original Obstacle Approaches")

    print("\nRunning new scenario (Obstacle Appears and Disappears)")
    run_case(scenario_obstacle_appears_and_disappears(), case_name="Obstacle Appears and Disappears")

    print("\nRunning new scenario (Obstacle Appears and Disappears)")
    run_case(scenario_obstacle_stays_and_disappears(), case_name="Obstacle Stays and Disappears")

if __name__ == "__main__":
    run_simulation()
