class AssumptionGenerator:
    def __init__(self, lts_model, property_p, interface_alphabet):
        """
        lts_model: your LTS object
        property_p: automaton / property to check
        interface_alphabet: set of actions in Σ
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
        Typically accepts traces that violate P.
        """
        # TODO: implement or call your method
        raise NotImplementedError

    def _compose(self, M, Perr):
        """
        Parallel composition: (M || Perr)
        """
        # TODO: implement composition
        raise NotImplementedError

    def _project_to_alphabet(self, lts, alphabet):
        """
        Project LTS to interface alphabet Σ: remove internal actions.
        """
        # TODO: implement projection
        raise NotImplementedError

    def _backward_error_propagation(self, lts):
        """
        Propagate error backward to find unsafe states.
        """
        # TODO: implement BEP
        raise NotImplementedError

    def _determinize(self, lts):
        """
        Determinize the LTS.
        """
        # TODO: implement determinization
        raise NotImplementedError

    def _complete_with_sink(self, lts):
        """
        Add sink state to complete the automaton.
        """
        # TODO: implement completion
        raise NotImplementedError

    def _error_removal(self, lts):
        """
        Remove error states and unreachable parts.
        """
        # TODO: implement removal
        raise NotImplementedError
