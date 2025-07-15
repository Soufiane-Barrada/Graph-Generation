import networkx as nx
import random
from graph_generator import GraphGenerator
from utils import construct_flattened_graph
from stepsVisualization import visualize_all_a_hop_neighborhoods, visualize_wl_labeling, visualize_procedural_generation, visualize_flattened_graph


if __name__ == "__main__":
    # Define the input graph and k_neighborhood K
    random.seed(6)
    K= 2
    G= nx.Graph()
    #edges= [(0, 1), (1, 2), (2, 3), (3, 4), (1, 5), (5, 6)]
    #edges= [(1, 2), (2, 3), (3, 4), (4, 5), (5, 2), (5, 3)]
    #edges= [(3,2), (3,4), (3,5), (3,1),(2,5)]
    #edges= [(1,2),(2,3),(3,4),(4,1)]
    #edges= [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,1)]
    edges= [(1,2),(2,4),(4,5),(1,3),(3,5),(5,6),(6,8),(8,9),(9,10),(10,7),(7,6)]
    G.add_edges_from(edges)

    # Instantiate a GraphGenerator
    graph_generator= GraphGenerator(G, k_neighborhood=K, wl_iterations=2*K)

    # Generate a graph (or many)
    generated_tiles= graph_generator.generate_graph(size=20)

    # Flatten the generated graph to a nx.Graph
    flattened_graph= construct_flattened_graph(generated_tiles)

    # Visualize the generated graph
    visualize_all_a_hop_neighborhoods(graph_generator.k_hop_subgraphs, graph_generator.k_neighborhood)
    color_map= visualize_wl_labeling(G, graph_generator.node_labels, graph_generator.label_mapping)
    visualize_flattened_graph(flattened_graph, color_map, colorful=True)