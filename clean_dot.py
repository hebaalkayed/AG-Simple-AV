def write_clean_clustered_dot(lts_json, dot_path):
    """
    Write a cleaner, clustered DOT file from an LTS JSON structure.

    Args:
        lts_json (dict): LTS dictionary with 'states' and 'transitions' keys.
        dot_path (str): File path to write the DOT file.
    """
    with open(dot_path, 'w') as f:
        f.write('digraph LTS {\n')
        f.write('  rankdir=TB;\n')  # top to bottom layout
        f.write('  node [shape=circle, fontsize=10, style=filled, fontname="Arial"];\n')
        f.write('  edge [fontsize=8, fontname="Arial"];\n\n')

        # Group states by mode prefix (before ||)
        clusters = {}
        for state in lts_json.get("states", []):
            mode = state.split("||")[0]
            clusters.setdefault(mode, []).append(state)

        # Write subgraph clusters
        for i, (mode, states) in enumerate(clusters.items()):
            f.write(f'  subgraph cluster_{i} {{\n')
            f.write(f'    label="{mode}";\n')
            f.write('    style=dashed;\n')
            f.write('    color=gray;\n')
            f.write('    fontcolor=black;\n')
            for s in states:
                color = "red" if "err" in s else "lightblue"
                f.write(f'    "{s}" [fillcolor={color}];\n')
            f.write('  }\n\n')

        # Write edges with simplified labels
        for t in lts_json.get("transitions", []):
            frm = t["from"]
            to = t["to"]
            action_full = t.get("action", "")
            # Simplify label: take first comma-separated part + "..." if longer
            action_label = action_full.split(",")[0]
            if len(action_full) > len(action_label):
                action_label += "..."
            # Escape quotes in labels
            action_label = action_label.replace('"', '\\"')
            f.write(f'  "{frm}" -> "{to}" [label="{action_label}"];\n')

        f.write('}\n')

    print(f"[INFO] Wrote clustered DOT file to: {dot_path}")

import json

# Load your LTS JSON file (replace with your actual file path)
with open("ControllerLTS_assumption.json", "r") as f:
    lts = json.load(f)

write_clean_clustered_dot(lts, "lts_clean.dot")

# Then run in your terminal:
# dot -Tpng lts_clean.dot -o lts_clean.png
