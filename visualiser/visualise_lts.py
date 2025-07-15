import networkx as nx
import matplotlib.pyplot as plt

MATPLOTLIB_COLOR_MAP = {
    "drive": "green",
    "coast": "gray",
    "brake": "orange",
    "emergency_brake": "yellow",
    "stopped": "red",
}

def visualise_lts(transitions):
    """
    Visualize an LTS given a list of transitions.
    Each transition is either:
      (source_state, action_label, target_state)
    or
      (source_state, action_label, target_state, state_label)
    """
    G = nx.MultiDiGraph()

    for t in transitions:
        if len(t) == 4:
            s1, action, s2, state_label = t
        elif len(t) == 3:
            s1, action, s2 = t
            state_label = None  # no color label available
        else:
            raise ValueError(f"Unexpected transition tuple length: {len(t)}")

        G.add_node(s1)
        G.add_node(s2)
        color = MATPLOTLIB_COLOR_MAP.get(state_label, "black")
        G.add_edge(s1, s2, label=action, color=color)

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=700)
    edges = G.edges()
    edge_colors = [edata['color'] for _, _, edata in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True)
    nx.draw_networkx_labels(G, pos, font_size=10)
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='gray')
    plt.title("Labelled Transition System (LTS)")
    plt.axis('off')
    plt.show()
