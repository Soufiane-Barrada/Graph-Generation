import networkx as nx
import matplotlib.pyplot as plt
import math



def visualize_all_a_hop_neighborhoods(a_hop_subgraphs, A):
    """
    Visualize all A-hop neighborhoods.
    """
    plt.figure(figsize=(15, 10))
    plt.suptitle(f"A-hop: {A}-hop Neighborhoods for All Nodes. ")
    
    grid_dims= int(math.ceil(math.sqrt(len(a_hop_subgraphs))))
    for i, (node, subgraph) in enumerate(a_hop_subgraphs.items()):
        plt.subplot(grid_dims, grid_dims, i + 1) 
        pos = nx.spring_layout(subgraph, seed=8)
        plt.title(f"Spanning Vertex {node}")
        node_colors = ['lightblue' if n != node else 'lightcoral' for n in subgraph.nodes()]
        nx.draw(subgraph, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=300, font_size=8)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()



def visualize_wl_labeling(graph, node_labels, label_mapping, save = False, file_name = "foo.pdf"):
    unique_labels = list(set(node_labels.values()))
    color_map = {label_mapping[label]: plt.cm.magma(i / len(unique_labels)) for i, label in enumerate(unique_labels)} # using a continuous colormap (because we don't know how many labels I would have)
    node_colors = [color_map[label_mapping[node_labels[node]]] for node in graph.nodes()]
    plt.figure(figsize=(15, 10))
    plt.suptitle(f"Labeled Input Graph")
    pos = nx.spring_layout(graph, seed=8)
    nx.draw(graph, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=300, font_size=8)
    for label, color in color_map.items():
        plt.scatter([], [], c=[color], label=f"Label {label}")
    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, loc='upper left')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if save:
        plt.savefig(file_name)
    plt.show()
    return color_map




def visualize_procedural_generation(generated_tiles, color_map):
    """Visualize the procedurally generated graph"""
    plt.figure(figsize=(15, 10))
    plt.suptitle("Procedural Graph Generation Output")
    tile_graph = nx.MultiGraph()
    uniqueid_to_label = {}

    for tile in generated_tiles:
        tile_graph.add_node(tile.unique_id)
        uniqueid_to_label[tile.unique_id] = tile.tile_label

    for tile in generated_tiles:
        for open_end, (other_tile, _) in tile.connections.items():
            tile_graph.add_edge(tile.unique_id, other_tile.unique_id)

    node_colors = [color_map.get(uniqueid_to_label[node]) for node in tile_graph.nodes]
    pos = nx.spring_layout(tile_graph, seed=8)
    nx.draw(tile_graph, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=300, font_size=8)
    
    
    plt.figure(figsize=(5, 5))
    for label, color in color_map.items():
        plt.scatter([], [], c=[color], label=f"Label {label}")
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, loc='center')
    plt.axis('off')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def visualize_flattened_graph(flattened_graph, color_map, colorful = False, save = False, file_name = "foo.pdf"):
    plt.figure(figsize=(15, 10))
    plt.suptitle("Flattened Graph")
    pos = nx.spring_layout(flattened_graph, seed=8)
    labels = nx.get_node_attributes(flattened_graph, 'label')
    node_colors = "lightblue"
    if colorful:
        node_colors = [color_map[label] for node_id, label in labels.items()]
    nx.draw(flattened_graph, pos, with_labels=True, labels=labels, node_color=node_colors, edge_color='gray', node_size=300, font_size=8)
    plt.tight_layout()
    if save:
        plt.savefig(file_name)
    plt.show()

    
