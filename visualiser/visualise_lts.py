import networkx as nx
import matplotlib.pyplot as plt

# Map your state labels to matplotlib-friendly colors
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
    Each transition is a tuple: (source_state, action_label, target_state, state_label)
    """
    G = nx.MultiDiGraph()
    
    # Add nodes and edges
    for s1, action, s2, state_label in transitions:
        G.add_node(s1)
        G.add_node(s2)
        G.add_edge(s1, s2, label=action, color=MATPLOTLIB_COLOR_MAP.get(state_label, "black"))
    
    pos = nx.spring_layout(G)  # layout for nodes
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)
    
    # Draw edges with colors
    edges = G.edges()
    edge_colors = [edata['color'] for _, _, edata in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True)
    
    # Draw node labels (state names)
    nx.draw_networkx_labels(G, pos, font_size=10)
    
    # Draw edge labels (actions)
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='gray')
    
    plt.title("Labelled Transition System (LTS)")
    plt.axis('off')
    plt.show()

# if __name__ == "__main__":
#     # Example transitions list: (from_state, action_label, to_state, state_label)
#     example_transitions = [
#         ("drive", "observe(obs1, 10.0)", "coast", "coast"),
#         ("coast", "observe(obs2, 5.0)", "brake", "brake"),
#         ("brake", "observe(obs3, 1.0)", "emergency_brake", "emergency_brake"),
#         ("emergency_brake", "observe(obs4, 0.0)", "stopped", "stopped"),
#     ]
    
#     visualise_lts(example_transitions)
