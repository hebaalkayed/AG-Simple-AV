# Autonomous Vehicle System Assume-Guarantee Verification Example

## Purpose

This repository abstractly models multiple components of a learning-enabled autonomous vehicle system—including controller, vehicle dynamics, and perception—as Labelled Transition Systems (LTS). It implements the **weakest assumption generation algorithm** from the paper:

> *Assumption Generation for the Verification of Learning-Enabled Autonomous Systems*  
> Pasareanu et al., 2023  
> [arXiv:2305.18372](https://arxiv.org/abs/2305.18372)

The goal is to support **compositional verification** of safety properties (e.g., collision avoidance) by generating weakest assumptions for each component’s environment.

---

## Project Components (so far)

- **LTS Mapper / Logger:** Builds and logs detailed LTS models for vehicle and controller components, including noisy sensor estimates, velocities, accelerations, and obstacle states.
- **LTS Visualiser:** Console-based colour-coded display of LTS transitions to aid human inspection.
- **LTS JSON Exporter:** Serialises LTS models and safety properties into JSON format suitable for further analysis or model checking.
- **Weakest Assumption Generator:** Implements the algorithm to produce weakest environment assumptions from the LTS and safety property JSON files.

---

## How to Run

1. **Run the main simulation:**

   This runs a scenario with noisy sensor inputs, generates LTS models for the controller and vehicle, prints coloured LTS transitions, visualises them in the console, and exports LTS JSON files.

   Run: python main.py

This executes predefined scenarios such as an obstacle approaching, simulating perception and control with noise.

2. **Generate weakest assumption:**

After running the simulation and generating the LTS JSON files (e.g., `controller_lts.json`), run the assumption generator: 
python assumption_generator.py


This reads the LTS JSON and property, applies the assumption generation algorithm, and outputs `controller_assumption.json`.

---

## Assumption Generation Algorithm

This project implements the **weakest environment assumption generation algorithm** as described in:

> *Assumption Generation for the Verification of Learning-Enabled Autonomous Systems*  
> (Pasareanu et al., 2023) – Algorithm III.1  
> [arXiv:2305.18372](https://arxiv.org/abs/2305.18372)

### 🧠 Purpose

The weakest assumption represents the **minimal set of environment behaviours** that ensure a given component (e.g., the controller) will satisfy a safety property. It supports **compositional verification**: once the assumption is generated, any environment (e.g., the vehicle) that satisfies it will guarantee the composed system satisfies the property.

Formally, for a component *M*, property *P*, and interface alphabet *Σ ⊆ Σ<sub>I</sub>*, the assumption *A<sup>w</sup><sub>Σ</sub>* ensures:

*M* &#124;&#124; *N* ⊨ *P* &nbsp;&nbsp;*if and only if*&nbsp;&nbsp; *N* ⊨ *A*<sup>w</sup><sub>Σ</sub>

---

### ⚙️ Algorithm Overview (Adapted from the Paper)

Given:
- an LTS model *M*,
- a safety property *P*,
- and an interface alphabet *Σ ⊆ Σ<sub>I</sub>*,

the algorithm builds the weakest assumption *A<sup>w</sup><sub>Σ</sub>* as follows:

1. **Build the Error Automaton:**  
   Construct *P<sub>err</sub>*, the automaton that accepts traces violating the property *P*.

2. **Compose the Model with the Error Automaton:**  
   Compute the synchronous product *M || P<sub>err</sub>*, then project it to the interface alphabet *Σ* to obtain *M′*.

3. **Backward Error Propagation:**  
   Perform backward propagation of the `err` state over transitions labeled with internal actions (`τ`) and actual variable updates. This identifies unsafe states from which error cannot be avoided.

4. **Determinisation:**  
   Convert *M′* into a deterministic automaton using subset construction. Sets of states that include `err` are treated as new `err` states, reflecting that any ambiguity about whether an error might occur leads to rejecting that behaviour.

5. **Completion with Sink:**  
   Add a special `sink` state and complete the transition relation so that every state has a defined transition for every action in *Σ*. Transitions not defined in the deterministic LTS lead to the sink.

6. **Error Removal:**  
   Finally, remove the `err` state and all transitions to or from it. The result is the weakest assumption *A<sup>w</sup><sub>Σ</sub>*, over alphabet *Σ*.

---

### 📌 Interpretation of the Assumption

The assumption describes **what the environment is allowed to do** to avoid leading the component to violate the property.

For example, the resulting assumption might restrict the vehicle to never exceed a certain deceleration value, e.g.:

> “The controller will remain safe **as long as** the vehicle never applies deceleration stronger than -8.0 m/s².”

The generated assumption is:
- **Deterministic:** Only one possible transition per action in each state.
- **Input-complete:** Every state handles every action in the interface alphabet (due to the sink).
- **Error-free:** All unsafe behaviours have been removed.

This makes the assumption suitable for automated verification and ensures it is the **weakest** such assumption — i.e., it constrains the environment no more than necessary.

---

## Status

- ✅ LTS logging, export, and visualisation implemented.
- ✅ Controller and vehicle simulation under noise.
- ✅ Weakest assumption generation pipeline (partial; determinisation in progress).
- 🔄 Next steps: Full determinisation implementation, pruning optimisations, support for multiple properties and interface alphabets.




