from abc import ABC, abstractmethod
import json

class TerminalColours:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    ORANGE = "\033[38;5;208m"
    DEFAULT = ""

STATE_COLOUR_MAP = {
    "drive": TerminalColours.GREEN,
    "coast": TerminalColours.DEFAULT,
    "brake": TerminalColours.ORANGE,
    "emergency_brake": TerminalColours.YELLOW,
    "stopped": TerminalColours.RED,
}

class BaseLTSBuilder(ABC):
    @abstractmethod
    def colour_line(self, line: str, **kwargs) -> str:
        pass

    @abstractmethod
    def log_step(self, i, state, **kwargs):
        pass

    def export_to_json(
        self,
        json_path="lts.json",
        name="UnnamedLTS",
        initial_state=None,
        property_dict=None
    ):
        """
        Export the LTS to JSON. Assumes subclass has get_transitions().
        """
        transitions_raw = self.get_transitions()

        # Collect unique states and actions
        states = set()
        actions = set()
        for from_state, label, to_state, _ in transitions_raw:
            states.add(from_state)
            states.add(to_state)
            actions.add(label)

        # Build transition list
        transitions = [
            {"from": from_state, "to": to_state, "action": label}
            for from_state, label, to_state, _ in transitions_raw
        ]

        # Determine initial state
        if initial_state is None:
            initial_state = getattr(self, 'current_state', None)
            if initial_state is None and transitions_raw:
                initial_state = transitions_raw[0][0]
        if initial_state is None:
            raise ValueError("Could not determine initial state; please pass it explicitly.")

        # Default empty property
        if property_dict is None:
            property_dict = {}

        # Build JSON
        lts_json = {
            "name": name,
            "states": sorted(states),
            "initial_state": initial_state,
            "transitions": transitions,
            "interface_alphabet": sorted(actions),
            "property": property_dict
        }

        # Write to file
        with open(json_path, "w") as f:
            json.dump(lts_json, f, indent=4)

        print(f"LTS '{name}' exported to {json_path}")
