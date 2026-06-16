import networkx as nx
import matplotlib.pyplot as plt

G = nx.MultiDiGraph()

G.add_nodes_from(['A', 'B', 'C', 'D'])

edges = [('A', 'B', {'label': 'Edge 1 (A to B)'}), ('A', 'C', {'label': 'Edge 2 (A to C)'}), 
         ('B', 'C', {'label': 'Edge 3 (B to C)'}), ('C', 'D', {'label': 'Edge 4 (C to D)'}), 
         ('B', 'A', {'label': 'Edge 5 (B to A)'}), ('A', 'A', {'label': ''})]
G.add_edges_from(edges)

pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos=pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=12, font_weight='bold', arrows=True)

edge_labels = {(source, target): data['label'] for source, target, data in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_color='red')

plt.show()
