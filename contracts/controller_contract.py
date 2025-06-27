# contracts/controller_contract.py

from contracts.base_contract import ComponentContract

class ControllerContract(ComponentContract):
    def __init__(self, max_acceleration=1.0, emergency_decel=-2.0):
        self.max_acceleration = max_acceleration
        self.emergency_decel = emergency_decel

    def get_assumptions(self):
        return {
            "perception_output in {0, 1}": "Valid obstacle classification",
            "obstacle_distance >= 0": "Non-negative distance to obstacle"
        }

    def get_guarantees(self):
        return {
            "acceleration <= 1.0": "Normal drive limit",
            "acceleration >= -2.0": "Emergency deceleration cap",
            "state transitions follow FSM": True
        }
