# contracts/perception_contract.py

from contracts.base_contract import ComponentContract

class PerceptionContract(ComponentContract):
    def get_assumptions(self):
        return {
            "input distance ∈ ℝ": "Receives continuous obstacle distance",
        }

    def get_guarantees(self):
        return {
            "output ∈ {0, 1}": "Discrete classification",
            "output = 1 if distance <= 9": "Perfect perception (configurable)"
        }
