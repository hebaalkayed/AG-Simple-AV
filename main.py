import torch
import time

from components.perception import SimplePerceptionNet, perfect_perception
from components.vehicle import Vehicle
from components.controller import Controller
from lts_builders.controller_lts_builder import ControllerLTSBuilder
from lts_builders.vehicle_lts_builder import VehicleLTSBuilder
from visualiser.visualise_lts import visualise_lts

def scenario_obstacle_approaches():
    return [max(0, 15 - step * 1.0) for step in range(18)]

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

    controller_lts_builder = ControllerLTSBuilder()
    vehicle_lts_builder = VehicleLTSBuilder(quantize=2)
    vehicle = Vehicle(vehicle_lts_builder)
    controller = Controller(vehicle, controller_lts_builder)

    dt = 0.2
    DEBUG = True

    for step, obstacle_distance in enumerate(obstacle_distances):
        perception_output = get_perception_output(obstacle_distance)

        steering, acceleration = controller.control(perception_output, obstacle_distance)
        vehicle.step(steering, acceleration, dt)

        if DEBUG:
            line = (
                f"Step {step} -  State {controller.state}, "
                f"Pos=({vehicle.x:.2f}, {vehicle.y:.2f}), "
                f"Vel(Actual)={vehicle.actual_velocity:.2f}, "
                f"Vel(Est)={controller.estimated_velocity:.2f}, "
                f"Perception={'Obstacle' if perception_output == 1 else 'Clear'}, "
                f"ObstacleDist={obstacle_distance:.2f}, "
                f"Acc(Actual)={vehicle.actual_acceleration:.2f}, "
                f"Acc(Req)={vehicle.requested_acceleration:.2f}, "
                f"Acc(Est)={controller.estimated_acceleration:.2f}"
            )
        else:
            line = (
                f"Step {step} -  State {controller.state}, "
                f"Pos=({vehicle.x:.2f}, {vehicle.y:.2f}), "
                f"Vel={vehicle.actual_velocity:.2f}, "
                f"Perception={'Obstacle' if perception_output == 1 else 'Clear'}, "
                f"ObstacleDist={obstacle_distance:.2f}, "
                f"Acc={acceleration:.2f}"
            )

        print(controller_lts_builder.colour_line(line, controller.state))
        time.sleep(0.1)

    controller_lts_builder.print_lts()
    vehicle_lts_builder.print_lts()
    visualise_lts(controller_lts_builder.get_transitions())
    visualise_lts(vehicle_lts_builder.get_transitions())

    controller_lts_builder.export_to_json(
        json_path="controller_lts.json",
        name="ControllerLTS",
        initial_state="drive",
        property_dict={
            "type": "safety",
            "description": "No collision: obstacle_distance must never be 0.0",
            "violation_condition": {
                 "field": "obstacle_distance",
                 "operator": "==",
                 "value": 0.0
            }      
        }
    )


def run_simulation():
    run_case(scenario_obstacle_approaches(), case_name="Original Obstacle Approaches")
    # run_case(scenario_obstacle_appears_and_disappears(), case_name="Obstacle Appears and Disappears")
    # run_case(scenario_obstacle_stays_and_disappears(), case_name="Obstacle Stays and Disappears")

if __name__ == "__main__":
    run_simulation()
