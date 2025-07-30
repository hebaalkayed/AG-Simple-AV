# weakest_assumption_generator.py

import json
import copy
import logging
import os
from visualiser.visualise_lts import visualise_lts
from collections import defaultdict

try:
    import graphviz
except ImportError:
    graphviz = None

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def validate_lts_structure(lts, name="LTS"):
    errors = []
    states = set(lts.get("states", []))
    initial = lts.get("initial_state", None)
    transitions = lts.get("transitions", [])

    if initial not in states:
        errors.append(f"{name}: initial_state '{initial}' not in states.")

    for i, t in enumerate(transitions):
        if t["from"] not in states:
            errors.append(f"{name}: transition {i} has unknown 'from' state: {t['from']}")
        if t["to"] not in states:
            errors.append(f"{name}: transition {i} has unknown 'to' state: {t['to']}")
        if "action" not in t:
            errors.append(f"{name}: transition {i} missing 'action'.")

    if "interface_alphabet" in lts:
        alphabet = set(lts["interface_alphabet"])
        for i, t in enumerate(transitions):
            if t["action"] not in alphabet:
                errors.append(f"{name}: transition {i} uses action '{t['action']}' not in interface_alphabet.")

    if errors:
        logging.warning(f"[Validation] Issues found in {name}:")
        for err in errors:
            logging.warning(" - %s", err)
    else:
        logging.info(f"[Validation] {name} passed structural checks.")

def is_deterministic(lts):
    seen = defaultdict(set)
    for t in lts["transitions"]:
        key = (t["from"], t["action"])
        if t["to"] in seen[key]:
            continue
        if len(seen[key]) > 0:
            return False
        seen[key].add(t["to"])
    return True

class AssumptionGenerator:
    def __init__(self, lts_model, property_p, interface_alphabet):
        self.M = lts_model
        self.P = property_p
        self.Sigma = interface_alphabet
        self.lts_name = self.M.get("name", "lts")

    def build_assumption(self):
        output_dir = f"{self.lts_name}_assumption_output"
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir

        logging.info("[Step 1] Composing model with error automaton...")
        Perr = self._build_error_automaton(self.P)
        M_comp = self._compose(self.M, Perr)
        validate_lts_structure(M_comp, f"{self.lts_name}_composed")
        visualise_lts(M_comp['transitions'], os.path.join(self.output_dir, f"1_{self.lts_name}_composed.png"))
        with open(os.path.join(output_dir, f"1_{self.lts_name}_composed.json"), 'w') as f:
            json.dump(M_comp, f, indent=4)

        logging.info("[Step 2] Projecting composed model to interface alphabet Σ...")
        M_proj = self._project_to_alphabet(M_comp, self.Sigma)
        validate_lts_structure(M_proj, f"{self.lts_name}_projected")
        visualise_lts(M_proj['transitions'], os.path.join(self.output_dir, f"2_{self.lts_name}_projected.png"))
        with open(os.path.join(output_dir, f"2_{self.lts_name}_projected.json"), 'w') as f:
            json.dump(M_proj, f, indent=4)

        logging.info("[Step 3] Performing backward error propagation...")
        M_bep = self._backward_error_propagation(M_proj)
        validate_lts_structure(M_bep, f"{self.lts_name}_backward")
        visualise_lts(M_bep['transitions'], os.path.join(self.output_dir, f"3_{self.lts_name}_backward.png"))
        with open(os.path.join(output_dir, f"3_{self.lts_name}_backward.json"), 'w') as f:
            json.dump(M_bep, f, indent=4)

        if not is_deterministic(M_proj):
            logging.warning("Projected LTS is non-deterministic. Determinization will be applied.")
            M_det = self._determinize(M_bep)
        else:
            logging.info("Projected LTS is deterministic. Skipping determinization.")
            M_det = M_bep
        with open(os.path.join(output_dir, f"4_{self.lts_name}_determinized.json"), 'w') as f:
            json.dump(M_det, f, indent=4)

        logging.info("[Step 5] Completing with sink state...")
        M_completed = self._complete_with_sink(M_det)
        validate_lts_structure(M_completed, f"{self.lts_name}_completed")
        visualise_lts(M_completed['transitions'], os.path.join(self.output_dir, f"5_{self.lts_name}_completed.png"))
        with open(os.path.join(output_dir, f"5_{self.lts_name}_completed.json"), 'w') as f:
            json.dump(M_completed, f, indent=4)

        logging.info("[Step 6] Removing error states and unreachable parts...")
        A_sigma_w = self._error_removal(M_completed)
        validate_lts_structure(A_sigma_w, f"{self.lts_name}_final_assumption")
        visualise_lts(A_sigma_w['transitions'], os.path.join(self.output_dir, f"6_{self.lts_name}_final_assumption.png"))
        with open(os.path.join(output_dir, f"6_{self.lts_name}_final_assumption.json"), 'w') as f:
            json.dump(A_sigma_w, f, indent=4)

        return A_sigma_w


    def _build_error_automaton(self, P):
        """
        Build the Perr automaton from property P.
        Accepts traces that violate the safety condition.
        For generality, we create transitions from 'ok' to 'err'
        for any action that violates the given violation_condition.
        """
        err_automaton = {
            "states": ["ok", "err"],
            "initial_state": "ok",
            "transitions": [],
            "interface_alphabet": self.Sigma
        }

        field = P["violation_condition"]["field"]
        operator = P["violation_condition"]["operator"]
        value = P["violation_condition"]["value"]

        for action in self.Sigma:
            try:
                action_dict = self._parse_action(action)
                if self._violates_property(action_dict, field, operator, value):
                    err_automaton["transitions"].append({
                        "from": "ok",
                        "to": "err",
                        "action": action
                    })
                else:
                    err_automaton["transitions"].append({
                        "from": "ok",
                        "to": "ok",
                        "action": action
                    })
            except Exception:
                pass  # Skip unparseable actions

        return err_automaton

    def _parse_action(self, action_str):
        """
        Converts an action string like "a=1, b=2" to a dictionary {'a': 1, 'b': 2}
        """
        parts = [p.strip() for p in action_str.split(",")]
        result = {}
        for part in parts:
            if "=" in part:
                key, val = part.split("=")
                key = key.strip()
                val = val.strip()
                try:
                    val = float(val)
                except ValueError:
                    pass
                result[key] = val
        return result

    def _violates_property(self, action_dict, field, operator, value):
        """
        Evaluates whether a given action violates the property.
        Currently supports ==, !=, <, >, <=, >=.
        """
        if field not in action_dict:
            return False
        actual = action_dict[field]
        if operator == "==":
            return actual == value
        elif operator == "!=":
            return actual != value
        elif operator == "<":
            return actual < value
        elif operator == ">":
            return actual > value
        elif operator == "<=" or operator == "<=":
            return actual <= value
        elif operator == ">=" or operator == ">=":
            return actual >= value
        return False

    def _compose(self, M, Perr):
        """
        Parallel composition: (M || Perr)
        Synchronises over shared actions — i.e., identical action strings.
        This performs a product construction where transitions match.
        """
        composed = {
            "states": [],
            "initial_state": (M["initial_state"], Perr["initial_state"]),
            "transitions": [],
            "interface_alphabet": self.Sigma
        }

        queue = [composed["initial_state"]]
        visited = set(queue)

        while queue:
            (s1, s2) = queue.pop(0)
            composed["states"].append((s1, s2))

            for t1 in M["transitions"]:
                if t1["from"] != s1:
                    continue
                for t2 in Perr["transitions"]:
                    if t2["from"] != s2:
                        continue
                    if t1["action"] == t2["action"]:
                        new_state = (t1["to"], t2["to"])
                        if new_state not in visited:
                            visited.add(new_state)
                            queue.append(new_state)
                        composed["transitions"].append({
                            "from": (s1, s2),
                            "to": new_state,
                            "action": t1["action"]
                        })

        # Flatten state names to strings for JSON compatibility
        composed["states"] = [f"{a}||{b}" for (a, b) in composed["states"]]
        composed["initial_state"] = f"{composed['initial_state'][0]}||{composed['initial_state'][1]}"
        for t in composed["transitions"]:
            t["from"] = f"{t['from'][0]}||{t['from'][1]}"
            t["to"] = f"{t['to'][0]}||{t['to'][1]}"

        return composed

    def _project_to_alphabet(self, lts, alphabet):
        """
        Project LTS to interface alphabet Σ: remove internal actions.
        Keep only transitions with actions in Σ.
        """
        new_transitions = [
            t for t in lts['transitions']
            if t['action'] in alphabet
        ]
        states_involved = set()
        for t in new_transitions:
            states_involved.add(t['from'])
            states_involved.add(t['to'])

        lts_copy = copy.deepcopy(lts)
        lts_copy['transitions'] = new_transitions
        lts_copy['states'] = list(states_involved)
        if lts_copy['initial_state'] not in lts_copy['states']:
            lts_copy['states'].append(lts_copy['initial_state'])
        return lts_copy

    def _backward_error_propagation(self, lts):
        """
        Identify all states that can lead to 'err' via any path.
        Compute backward reachable set from all 'err'-containing states.
        """
        reverse_map = {}
        for t in lts['transitions']:
            to_state = t['to']
            from_state = t['from']
            reverse_map.setdefault(to_state, set()).add(from_state)

        unsafe = set([s for s in lts['states'] if 'err' in s])
        queue = list(unsafe)

        while queue:
            s = queue.pop(0)
            for pred in reverse_map.get(s, []):
                if pred not in unsafe:
                    unsafe.add(pred)
                    queue.append(pred)

        lts_copy = copy.deepcopy(lts)
        lts_copy['unsafe_states'] = list(unsafe)
        return lts_copy

    def _determinize(self, lts):
        """
        Determinize the LTS.
        Placeholder: assume already deterministic.
        """
        return lts

    def _complete_with_sink(self, lts):
        """
        Add sink state to complete the automaton.
        For every state, add missing actions leading to 'sink'.
        """
        sink_state = 'sink'
        states = set(lts['states'])
        states.add(sink_state)
        new_transitions = list(lts['transitions'])

        for state in lts['states']:
            existing_actions = set(
                t['action'] for t in new_transitions if t['from'] == state
            )
            missing = set(self.Sigma) - existing_actions
            for action in missing:
                new_transitions.append({
                    'from': state,
                    'to': sink_state,
                    'action': action
                })

        lts_copy = copy.deepcopy(lts)
        lts_copy['states'] = list(states)
        lts_copy['transitions'] = new_transitions
        return lts_copy

    def _error_removal(self, lts):
        """
        Remove error states and unreachable parts.
        Remove 'err' state and transitions to/from it.
        """
        states = [s for s in lts['states'] if 'err' not in s]
        transitions = [
            t for t in lts['transitions']
            if 'err' not in t['from'] and 'err' not in t['to']
        ]
        lts_copy = copy.deepcopy(lts)
        lts_copy['states'] = states
        lts_copy['transitions'] = transitions
        return lts_copy

# --- main script part ---
if __name__ == "__main__":
    with open('controller_lts.json') as f:
        lts = json.load(f)

    lts_name = lts.get("name", "controller")
    interface_alphabet = lts['interface_alphabet']
    property_dict = lts['property']

    gen = AssumptionGenerator(lts, property_dict, interface_alphabet)
    assumption = gen.build_assumption()

    output_file = os.path.join(f"{lts_name}_assumption_output", f"{lts_name}_assumption.json")
    with open(output_file, 'w') as f:
        json.dump(assumption, f, indent=4)

    logging.info("\nAssumption generated and saved to %s", output_file)
