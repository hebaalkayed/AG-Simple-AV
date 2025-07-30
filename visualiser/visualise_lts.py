import networkx as nx
import matplotlib.pyplot as plt
import textwrap
import os

MATPLOTLIB_COLOR_MAP = {
    "drive": "green",
    "coast": "gray",
    "brake": "orange",
    "emergency_brake": "yellow",
    "stopped": "red",
}

def wrap_label(text, width=25):
    """Wrap long edge labels for better display"""
    return "\n".join(textwrap.wrap(text, width))

def visualise_lts(transitions, save_path=None):
    """
    Visualise an LTS with labelled transitions and execution numbers.
    Each transition is (s1, label, s2) or (s1, label, s2, state_label).

    If save_path is given, save the plot as a PNG file there.
    """
    G = nx.MultiDiGraph()
    plt.figure(figsize=(12, 8))
    edge_labels = {}
    edge_styles = {}

    for i, t in enumerate(transitions):
        # Ensure correct dictionary format
        if isinstance(t, dict) and all(k in t for k in ("from", "to", "action")):
            s1 = t["from"]
            s2 = t["to"]
            action = t["action"]
            state_label = s1.split("||")[1] if "||" in s1 else None
        elif isinstance(t, tuple) and len(t) in (3, 4):
            if len(t) == 4:
                s1, action, s2, state_label = t
            else:
                s1, action, s2 = t
                state_label = None
        else:
            raise ValueError(f"Unexpected transition format: {t}")

        # Build edge label with step number and wrapped action
        step_num = i + 1
        numbered_label = f"#{step_num}\n{wrap_label(action)}"

        # Assign colour based on label (ok/err/etc.)
        color = MATPLOTLIB_COLOR_MAP.get(state_label, "black")

        # Add nodes and edge with a unique key to preserve multiple transitions
        G.add_node(s1)
        G.add_node(s2)
        key = f"{s1}->{s2}#{step_num}"
        G.add_edge(s1, s2, key=key, label=numbered_label, color=color, rad=0.05 * step_num)

        edge_labels[(s1, s2, key)] = numbered_label
        edge_styles[(s1, s2, key)] = (color, 0.05 * step_num)

    try:
        pos = nx.kamada_kawai_layout(G)
    except ImportError:
        print("[INFO] scipy not found. Falling back to spring_layout.")
        pos = nx.spring_layout(G, seed=42)

    node_colors = [MATPLOTLIB_COLOR_MAP.get(n, 'lightblue') for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800)
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Draw edges with custom curvature
    for (u, v, k), (color, rad) in edge_styles.items():
        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(u, v)],
            edge_color=color,
            connectionstyle=f'arc3,rad={rad}',
            arrows=True
        )

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='gray')

    plt.title("Labelled Transition System (Sequential Trace)")
    plt.axis('off')
    plt.tight_layout()

    if save_path:
        cwd = os.getcwd()  # current working directory
        save_path = os.path.join(cwd, save_path)
        plt.savefig(save_path, format='png', dpi=300)
        print(f"[INFO] Saved LTS visualisation to {save_path}")
        
    plt.close()  # important to free the figure so next call is clean

    # plt.show()
