# assumption_generator.py

import json
import copy

class AssumptionGenerator:
    def __init__(self, lts_model, property_p, interface_alphabet):
        """
        lts_model: your LTS object (dict)
        property_p: dict describing the property
        interface_alphabet: list of actions in Σ
        """
        self.M = lts_model
        self.P = property_p
        self.Sigma = interface_alphabet

    def build_assumption(self):
        """
        Implements:
        M′ := (M || Perr )↓Σ  
        M′′ := BackwardErrorPropagation(M′)
        AeΣrr := Determinization(M′′)
        ÂeΣrr := CompletionWithSink(AeΣrr)
        AΣw := ErrorRemoval(ÂeΣrr)
        """
        # Step 1: Compose with Perr (error automaton from P)
        Perr = self._build_error_automaton(self.P)
        M_comp = self._compose(self.M, Perr)

        # Step 2: Project to interface alphabet Σ
        M_proj = self._project_to_alphabet(M_comp, self.Sigma)

        # Step 3: Backward error propagation
        M_bep = self._backward_error_propagation(M_proj)

        # Step 4: Determinization
        M_det = self._determinize(M_bep)

        # Step 5: Completion with sink
        M_completed = self._complete_with_sink(M_det)

        # Step 6: Error removal
        A_sigma_w = self._error_removal(M_completed)

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
                # Ignore unparseable actions
                pass

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
        elif operator == "<=":
            return actual <= value
        elif operator == ">=":
            return actual >= value
        return False

    def _compose(self, M, Perr):
        """
        Parallel composition: (M || Perr)
        We synchronise over shared actions — i.e., identical action strings.
        This performs a product construction and only advances both
        systems together when actions match.
        """
        composed = {
            "states": [],
            "initial_state": (M["initial_state"], Perr["initial_state"]),
            "transitions": [],
            "interface_alphabet": self.Sigma
        }

        # BFS-style product state generation
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
        Identify all states that can lead to 'err' via any path (i.e., unsafe states).
        We do this by computing the backward reachable set from all 'err'-containing states.
        """
        # Build reverse transition map: to_state -> list of from_states
        reverse_map = {}
        for t in lts['transitions']:
            to_state = t['to']
            from_state = t['from']
            reverse_map.setdefault(to_state, set()).add(from_state)

        # Start from all states containing 'err'
        unsafe = set([s for s in lts['states'] if 'err' in s])
        queue = list(unsafe)

        # Perform backward reachability: add all predecessors that lead to an unsafe state
        while queue:
            s = queue.pop(0)
            for pred in reverse_map.get(s, []):
                if pred not in unsafe:
                    unsafe.add(pred)
                    queue.append(pred)

        # Create a new LTS that keeps all transitions and states
        # (we don't eliminate anything here; just mark unsafe states)
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

    interface_alphabet = lts['interface_alphabet']
    property_dict = lts['property']

    gen = AssumptionGenerator(lts, property_dict, interface_alphabet)
    assumption = gen.build_assumption()

    with open('controller_assumption.json', 'w') as f:
        json.dump(assumption, f, indent=4)

    print("Assumption generated and saved to controller_assumption.json")
