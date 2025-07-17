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
        M_comp = self._compose(self.M, self._build_error_automaton(self.P))

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
        Typically accepts traces that violate P.
        For now: simulate Perr as a single 'err' state.
        """
        return {
            "states": ["ok", "err"],
            "initial_state": "ok",
            "transitions": [],
            "interface_alphabet": self.Sigma
        }

    def _compose(self, M, Perr):
        """
        Parallel composition: (M || Perr) -- composed via synchronous product over shared action  (e.g., observe(...)).
        For now: just return M unchanged.
        """
        # Proper composition is complex; skip for small example.
        return copy.deepcopy(M)

    def _project_to_alphabet(self, lts, alphabet):
        """
        Project LTS to interface alphabet Σ: remove internal actions.
        Keep only transitions with actions in Σ.
        """
        new_transitions = [
            t for t in lts['transitions']
            if t['action'] in alphabet
        ]
        lts_copy = copy.deepcopy(lts)
        lts_copy['transitions'] = new_transitions
        return lts_copy

    def _backward_error_propagation(self, lts):
        """
        Propagate error backward to find unsafe states.
        Placeholder: return as is.
        """
        return lts

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
        states = [s for s in lts['states'] if s != 'err']
        transitions = [
            t for t in lts['transitions']
            if t['from'] != 'err' and t['to'] != 'err'
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
