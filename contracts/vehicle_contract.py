# contracts/vehicle_contract.py

from contracts.base_contract import ComponentContract

class VehicleContract(ComponentContract):
    def get_assumptions(self):
        return {
            "steering angle in [-π/4, π/4]": "Safe lateral control",
            "acceleration in [-2.0, 1.0]": "Within expected limits"
        }

    def get_guarantees(self):
        return {
            "velocity >= 0": "No reverse motion",
            "stopped implies acceleration = 0": "No updates when stopped",
            "x/y updated according to model": True
        }
