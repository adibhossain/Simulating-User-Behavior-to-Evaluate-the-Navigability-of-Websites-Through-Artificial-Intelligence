import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

#G.add_nodes_from(['A', 'B', 'C', 'D'])

# G.add_edges_from(edges)
G.add_edges_from([('Start', 'Home', {'label': '0'}), ('Home', 'Fishes', {'label': '1'}), ('Fishes', 'Seawater Fishes', {'label': '2'}), ('Seawater Fishes', 'Tuna', {'label': '3'}), ('Tuna', 'End', {'label': '4'})])
# G.add_edges_from([('Start', 'Home', {'label': '0'}), ('Home', 'Fishes', {'label': '1'}), ('Fishes', 'Freshwater Fishes', {'label': '2'}), ('Freshwater Fishes', 'Trout', {'label': '3'}), ('Freshwater Fishes', 'Catfish', {'label': '4'}), ('Fishes', 'Seawater Fishes', {'label': '5'}), ('Seawater Fishes', 'Tuna', {'label': '6'}), ('Tuna', 'End', {'label': '7'})])

pos = pos = nx.circular_layout(G)
nx.draw(G, pos=pos, with_labels=True, node_size=1500, node_color='white', font_size=10, font_weight='bold', node_shape='s', alpha=0.5)

edge_labels = nx.get_edge_attributes(G, 'label')
# nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_color='red', font_size=7)
nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_color='red', font_size=10)

plt.show()
