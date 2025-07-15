from collections import deque
import networkx as nx


def is_set(x, n):
    mask= 1 << n
    return x & mask != 0


def is_tile_graph_valid(newly_added_tile, label_mapping, A, num_iterations):
    ret=True
    visited= set()
    bfs_queue= deque()
    bfs_queue.appendleft((newly_added_tile, 0))
    visited.add(newly_added_tile)

    while(len(bfs_queue) > 0 and ret):
        tile_distance_pair= bfs_queue.pop()
        current_tile= tile_distance_pair[0]
        distance= tile_distance_pair[1]

        ret= is_tile_neighborhood_valid(current_tile, label_mapping, A, num_iterations)

        if(distance < A):
            for connection in current_tile.connections.values():
                neighbor_tile= connection[0]
                if neighbor_tile not in visited:
                    visited.add(neighbor_tile)
                    bfs_queue.appendleft((neighbor_tile, distance+1))

    return ret


def is_tile_neighborhood_valid(tile, label_mapping, A, num_iterations):

    flattened_subgraph = nx.Graph()
    visited= set()
    bfs_queue= deque()
    bfs_queue.appendleft((tile, 0))
    visited.add(tile)
    flattened_subgraph.add_node(tile.unique_id, label=tile.tile_label)

    while(len(bfs_queue) > 0):
        tile_distance_pair= bfs_queue.pop()
        current_tile= tile_distance_pair[0]
        distance= tile_distance_pair[1]

        if(distance < A):
            for connection in current_tile.connections.values():
                neighbor_tile= connection[0]
                if neighbor_tile not in visited:
                    visited.add(neighbor_tile)
                    bfs_queue.appendleft((neighbor_tile, distance+1))
                    flattened_subgraph.add_node(neighbor_tile.unique_id, label=neighbor_tile.tile_label)
                flattened_subgraph.add_edge(current_tile.unique_id, neighbor_tile.unique_id)
    
    return tile.is_subgraph_of_tile(flattened_subgraph, num_iterations, label_mapping)
        

def construct_flattened_graph(generated_tiles):
    """
    Constructs a flattened NetworkX graph from a list of tiles.
    """
    flattened_graph = nx.Graph()

    # Add nodes to the graph
    for tile in generated_tiles:
        flattened_graph.add_node(tile.unique_id, label=tile.tile_label)

    # Add edges based on connections
    added_edges = set()
    for tile in generated_tiles:
        for open_end, (connected_tile, connected_open_end) in tile.connections.items():
            edge = (tile.unique_id, connected_tile.unique_id)
            # Avoid adding duplicate edges
            if edge not in added_edges and (connected_tile.unique_id, tile.unique_id) not in added_edges:
                flattened_graph.add_edge(tile.unique_id, connected_tile.unique_id)
                added_edges.add(edge)

    return flattened_graph

