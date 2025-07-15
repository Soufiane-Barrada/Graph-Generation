from collections import deque
import networkx as nx
from utils import is_set


def extract_k_hop_neighborhoods(graph, k_neighborhood):
    """Extract k-hop neighborhood subgraphs for each node in the graph. the code assumes that the Networkx nodes of 'graph' are all intergers that start from 0, or 1"""
    k_hop_subgraphs = {}
    # we perform a BFS for each node to a maximum depth of k_neighborhood for each node to get it's corresponding k-hop neighborhood.
    for node in graph.nodes():
        queue= deque()
        queue.append((node,0)) # (node, distance from central node)
        subgraph = nx.Graph()
        subgraph.add_node(node)
        
        #BFS on current node
        while len(queue)>0:
            poped_node= queue.popleft()
            if poped_node[1] >= k_neighborhood:
                continue
            for neighbor in graph.neighbors(poped_node[0]):
                subgraph.add_edge(poped_node[0], neighbor)
                queue.append((neighbor,poped_node[1]+1))


        k_hop_subgraphs[node] = subgraph
    return k_hop_subgraphs
    



def wl_labeling(graph, spanning_vertex, num_iterations=5):
    """ Computes WL label for 'spanning_vertex'."""
    labels = {node: 1 for node in graph.nodes()}  # Initial label for all nodes
    labels[spanning_vertex] = 0
    
    for _ in range(num_iterations):
        # Update labels based on neighbors' labels
        new_labels = {}
        for node in graph.nodes():
            neighbor_labels = sorted([labels[neighbor] for neighbor in graph.neighbors(node)])
            new_labels[node] = hash((labels[node], tuple(neighbor_labels)))  # Create new hash as the label
        labels = new_labels
    
    return labels[spanning_vertex]




def _all_subgraph_labelings(graph, spanning_vertex, num_iterations):
    """ computes WL label for 'spanning_vertex', as well as all its possible labels in each possible subgraph of 'graph' """
    
    all_subgraph_labels=set()
    # First we compute the label with the full graph
    full_graph_label= wl_labeling(graph, spanning_vertex, num_iterations)
    all_subgraph_labels.add(full_graph_label)

    graph_size= graph.number_of_nodes()
    graph_nodes= set(graph.nodes())
    # The spanning vertex should always be part of any subgraph
    graph_nodes.remove(spanning_vertex)
    
    #assign to each node in the graph a bit position
    bit_to_node=[-1]*(graph_size-1)
    for bit_position, node in enumerate(graph_nodes):
        bit_to_node[bit_position]= node

    #loop through all possible subset of nodes of this graph
    num_subsets= 1<<(graph_size-1)
    for node_subset_bitList in range(1, num_subsets):
        subgraph= graph.copy()
        #Generate the current subgraph
        for bit_idx in range(0,graph_size-1):
            if not is_set(node_subset_bitList, bit_idx):
                subgraph.remove_node(bit_to_node[bit_idx])
        
        # We only consider connected subgraphs 
        if nx.number_connected_components(subgraph)==1:
            all_subgraph_labels.add(wl_labeling(subgraph, spanning_vertex, num_iterations))
    

    return full_graph_label, all_subgraph_labels

#*************************************************************************************************
from itertools import chain, combinations

def all_subgraph_labelings(graph, spanning_vertex, num_iterations):
    """Computes WL label for 'spanning_vertex', as well as all its possible labels in each possible subgraph of 'graph'."""
    
    all_subgraph_labels = set()
    
    # Compute label with the full graph
    full_graph_label = wl_labeling(graph, spanning_vertex, num_iterations)
    all_subgraph_labels.add(full_graph_label)

    graph_nodes = set(graph.nodes())
    graph_edges = set(graph.edges())
    
    # Ensure the spanning vertex is always in any subgraph
    graph_nodes.remove(spanning_vertex)

    # Generate all subsets of nodes that include the spanning vertex
    node_subsets = chain.from_iterable(combinations(graph_nodes, r) for r in range(len(graph_nodes) + 1))

    for node_subset in node_subsets:
        node_subset = set(node_subset) | {spanning_vertex}  # Always include the spanning vertex

        # Extract valid edges within this node subset
        valid_edges = {(u, v) for u, v in graph_edges if u in node_subset and v in node_subset}

        # Generate all edge subsets (including empty set)
        edge_subsets = chain.from_iterable(combinations(valid_edges, r) for r in range(len(valid_edges) + 1))

        for edge_subset in edge_subsets:
            subgraph = nx.Graph()
            subgraph.add_nodes_from(node_subset)
            subgraph.add_edges_from(edge_subset)

            # We only consider connected subgraphs
            if nx.is_connected(subgraph):
                all_subgraph_labels.add(wl_labeling(subgraph, spanning_vertex, num_iterations))

    return full_graph_label, all_subgraph_labels


