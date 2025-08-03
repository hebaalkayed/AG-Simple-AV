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

def wrap_label(label, items_per_line=2):
    """
    Wrap long edge labels for better readability by splitting on commas.
    """
    parts = label.split(", ")
    wrapped = "\n".join(
        [", ".join(parts[i:i + items_per_line]) for i in range(0, len(parts), items_per_line)]
    )
    return wrapped

def visualise_lts(transitions, save_path=None):
    """
    Visualise an LTS with labelled transitions and execution numbers.
    Each transition can be a dict with keys 'from', 'to', 'action' or a tuple.
    """
    G = nx.MultiDiGraph()
    plt.figure(figsize=(14, 10))  # Slightly bigger figure

    edge_labels = {}
    edge_styles = {}

    # Build the graph from transitions
    for i, t in enumerate(transitions):
        if isinstance(t, dict) and all(k in t for k in ("from", "to", "action")):
            s1 = t["from"]
            s2 = t["to"]
            action = t["action"]
            # Get the label part after "||" for color
            state_label = s1.split("||")[1] if "||" in s1 else None
        elif isinstance(t, tuple) and len(t) in (3, 4):
            if len(t) == 4:
                s1, action, s2, state_label = t
            else:
                s1, action, s2 = t
                state_label = None
        else:
            raise ValueError(f"Unexpected transition format: {t}")

        step_num = i + 1
        numbered_label = f"#{step_num}\n{wrap_label(action, items_per_line=3)}"  # Wrap more per line for less height

        color = MATPLOTLIB_COLOR_MAP.get(state_label, "black")

        G.add_node(s1)
        G.add_node(s2)

        key = f"{s1}->{s2}#{step_num}"
        G.add_edge(s1, s2, key=key, label=numbered_label, color=color, rad=0.1 * (step_num % 5))  # less curvature

        edge_labels[(s1, s2, key)] = numbered_label
        edge_styles[(s1, s2, key)] = (color, 0.1 * (step_num % 5))

    # Use a layout that spreads nodes nicely for sequential or hierarchical data
    try:
        pos = nx.spring_layout(G, seed=42, k=1.2, iterations=100)  # More iterations & spacing
    except ImportError:
        print("[INFO] scipy not found. Falling back to spring_layout.")
        pos = nx.spring_layout(G, seed=42)

    # Use color for nodes based on label part before "||"
    node_colors = [
        MATPLOTLIB_COLOR_MAP.get(n.split("||")[0], 'lightblue') for n in G.nodes()
    ]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')

    # Draw edges with curvature and color coding
    for (u, v, k), (color, rad) in edge_styles.items():
        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(u, v)],
            edge_color=color,
            connectionstyle=f'arc3,rad={rad}',
            arrows=True,
            arrowstyle='-|>',
            arrowsize=15,
            width=1.5,
            alpha=0.8,
        )

    # Edge labels in smaller font & gray for subtlety
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=7,
        font_color='dimgray',
        label_pos=0.5,  # center on edge
    )

    plt.title("Labelled Transition System (Sequential Trace)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()

    if save_path:
        cwd = os.getcwd()
        save_path = os.path.join(cwd, save_path)
        plt.savefig(save_path, format='png', dpi=300)
        print(f"[INFO] Saved LTS visualisation to {save_path}")

    plt.close()
