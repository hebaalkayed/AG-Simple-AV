# contracts/base_contract.py

from abc import ABC, abstractmethod

class ComponentContract(ABC):
    @abstractmethod
    def get_assumptions(self):
        pass

    @abstractmethod
    def get_guarantees(self):
        pass

    def check_contract(self):
        # Optional: print assumptions and guarantees
        print(f"Assumptions: {self.get_assumptions()}")
        print(f"Guarantees: {self.get_guarantees()}")
