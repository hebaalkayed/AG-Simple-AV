# Autonomous Vehicle System Assume-Guarantee Verification Example

## Purpose

This repository abstractly models multiple components of a learning-enabled autonomous vehicle system—including controller, vehicle dynamics, and perception—as Labelled Transition Systems (LTS). It briefly touches on the **assumption generation algorithm** from the paper:

> [*Assumption Generation for the Verification of Learning-Enabled Autonomous Systems* (Pasareanu et al.)](https://arxiv.org/abs/2305.18372)

The goal is to support **compositional verification** of safety properties (e.g., collision avoidance) by generating weakest assumptions for each component’s environment.

---

## Project Components(so far)

- **LTS Mapper / Logger:** Builds and logs detailed LTS models for vehicle and controller components, including noisy sensor estimates, velocities, accelerations, and obstacle states.
- **LTS Visualiser:** Console-based colour-coded display of LTS transitions to aid human inspection.
- **LTS JSON Exporter:** Serialises LTS models and safety properties into JSON format suitable for further analysis or model checking.
- **Weakest Assumption Generator:** Implements the algorithm to produce weakest environment assumptions from the LTS and safety property JSON files.

---

## Status

- Work in progress.
- Current focus: refining component models, realistic sensor noise, and simple assumption generation.

---

## How to Run

1. **Run the main simulation:**

   This runs a scenario with noisy sensor inputs, generates LTS models for the controller and vehicle, prints coloured LTS transitions, visualises them in the console, and exports LTS JSON files.

   ```bash
   python main.py

This executes predefined scenarios such as an obstacle approaching, simulating perception and control with noise.

2. **Generate weakest assumption:**

After running the simulation and generating the LTS JSON files (e.g., `controller_lts.json`), run the assumption generator:

```bash
python assumption_generator.py

This reads the LTS JSON and property, applies the assumption generation algorithm, and outputs controller_assumption.json.
