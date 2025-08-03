import json


def export_lts_to_dot(lts_json, dot_filename="lts.dot", simplify_labels=True):
    """
    Export an LTS JSON (with states, transitions) to a Graphviz DOT file.

    Args:
        lts_json: dict loaded from your LTS JSON file.
        dot_filename: output .dot filename.
        simplify_labels: if True, abbreviate transition labels for readability.
    """
    with open(dot_filename, "w") as f:
        f.write("digraph LTS {\n")
        f.write('  rankdir=TB;\n')  # top to bottom layout
        f.write('  node [shape=circle, fontsize=12];\n')

        # Add nodes
        for state in lts_json.get("states", []):
            # Mark initial state with doublecircle
            shape = "doublecircle" if state == lts_json.get("initial_state") else "circle"
            f.write(f'  "{state}" [shape={shape}];\n')

        # Add edges
        for t in lts_json.get("transitions", []):
            src = t["from"]
            dst = t["to"]
            label = t["action"]
            if simplify_labels:
                # Simplify by showing only first two comma-separated items, add "..."
                parts = label.split(", ")
                simple_label = ", ".join(parts[:2]) + ("..." if len(parts) > 2 else "")
            else:
                simple_label = label.replace('"', '\\"')  # escape quotes if any
            f.write(f'  "{src}" -> "{dst}" [label="{simple_label}", fontsize=10];\n')

        f.write("}\n")

    print(f"[INFO] DOT file saved to {dot_filename}")

with open("ControllerLTS_assumption.json") as f:
    lts_data = json.load(f)

export_lts_to_dot(lts_data, dot_filename="lts.dot")