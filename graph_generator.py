import random
import math
from collections import defaultdict
from tile_graph import TileGraph
from tile import Tile
from graph_labelling import extract_k_hop_neighborhoods, all_subgraph_labelings
from utils import is_tile_graph_valid


class GraphGenerator:
    def __init__(self, graph, k_neighborhood, wl_iterations):
        self.graph= graph
        self.k_neighborhood= k_neighborhood
        self.wl_iterations= wl_iterations
        self.k_hop_subgraphs= extract_k_hop_neighborhoods(self.graph, self.k_neighborhood)
        self.node_labels, self.node_subgraphs_labels, self.label_mapping= self._generate_wl_labels(self.k_hop_subgraphs, self.wl_iterations)
        neighbors= self._extract_label_neighborhoods(self.graph, self.node_labels, self.label_mapping)
        self.tile_library= self._create_tile_library(neighbors)
        self.auxiliary_structure= self._precompute_possible_connections(self.tile_library)

    def _generate_wl_labels(self, k_hop_subgraphs, wl_iterations):
        """
        Generate Weisfeiler-Lehman labels for the nodes in the graph based on k_neighborhood-hop neighborhoods, and all of their respective subgraph wl labelings.
        """
        node_labels = {}
        node_subgraphs_labels = {}
        label_mapping = {}
        all_labels = set()
        
        for node, subgraph in k_hop_subgraphs.items():
            node_label, all_subgraph_labels = all_subgraph_labelings(subgraph, node, num_iterations=wl_iterations)
            node_labels[node] = node_label
            node_subgraphs_labels[node] = all_subgraph_labels
            all_labels.update(all_subgraph_labels)

        # Assign labels to nodes in the graph (map the large hash values produced by the WL-labeling to simple incremebtal integers)
        assigned_label = 1
        for label in set(node_labels.values()):
            label_mapping[label] = assigned_label
            assigned_label += 1

        # Assign labels to all possible subgraphs of our tiles (map the large hash values to simple integers) 
        remaining_labels = all_labels.difference(label_mapping)
        for label in remaining_labels:
            label_mapping[label] = assigned_label
            assigned_label += 1

        return node_labels, node_subgraphs_labels, label_mapping

    def _create_tile_library(self, neighbors):
        """
        Create library of tiles based on node labels and their neighbors.
        """
        tile_library = defaultdict(list)
        for node, list_possible_neighbors in neighbors.items():
            set_of_subgraphs = set(map(lambda label: self.label_mapping[label], self.node_subgraphs_labels[node]))
            for open_end in list_possible_neighbors:
                tile = Tile(
                    tile_label=self.label_mapping[self.node_labels[node]],
                    original_node_id=node,
                    open_ends=open_end,
                    set_of_subgraphs=set_of_subgraphs
                )
                tile_library[tile.tile_label].append(tile)
        return tile_library

    def _precompute_possible_connections(self, tile_library):
        """
        Precompute possible connections for all Tiles. (For each Tile's open end, we find all tiles it can connect to.)
        return
        auxiliary_structure: {tile -> {open_end -> list(Tile)}}
        """
        auxiliary_structure = {}
        # For all different tiles with the same tile label
        for tile_label, tiles_list in tile_library.items():
            for tile in tiles_list:
                auxiliary_mapping = defaultdict(list)
                for open_end in tile.open_ends:
                    list_candidates = tile_library[open_end[0]]
                    for candidate_tile in list_candidates:
                        if tile_label in candidate_tile.list_of_neighbor_labels:
                            auxiliary_mapping[open_end].append(candidate_tile)
                auxiliary_structure[tile] = auxiliary_mapping

        return auxiliary_structure

    def _extract_label_neighborhoods(self, graph, node_labels, label_mapping):
        """ 
        Extract for each node in the Input graph, its neighbors and their corresponding label.
        return
        neighbors: {node -> list((neighbor_node_label, neighbor_node))}
        """
        neighbors = defaultdict(list)
        
        for node in graph.nodes():
            open_ends = []
            for neighbor in graph.neighbors(node):
                external_label = label_mapping[node_labels[neighbor]]
                open_ends.append((external_label, neighbor))
            neighbors[node].append(open_ends)
        
        return neighbors
    
    def _procedural_graph_generation(self, p, size=None):
        """
        Implements the Procedural Graph Generation PGG algorithm 
        """
        tile_graph= TileGraph()

        #Start with a random Tile
        first_tile_type = random.choice(random.choice(list(self.tile_library.values())))
        first_tile_instance = first_tile_type.clone_with_unique_id(unique_id= tile_graph.get_count_generated_tiles()+1)
        tile_graph.add_tile(first_tile_instance)

        #counter of failed validation steps
        count = 0

        #continue generation as long as there are open ends in our generated graph
        while tile_graph.still_open_tiles():
            
            count_generated_tiles= tile_graph.get_count_generated_tiles()
            if size is not None:
                try:
                    p = math.exp(-(size - count_generated_tiles)) * (len(tile_graph.get_open_tiles())/count_generated_tiles)
                except OverflowError:
                    p = 1

            # pick a random tile
            current_tile = random.choice(tile_graph.get_open_tiles())

            # pick an open end
            open_end = random.choice(current_tile.open_ends)

            # Decide whether to connect to an existing tile (probability p)
            if random.random() < p and count_generated_tiles > 1:
                found = False
                for other_tile in tile_graph.get_open_tiles():

                    if found:
                        break

                    # Do not connect a tile to itself
                    if other_tile.unique_id == current_tile.unique_id:
                        continue
                    
                    other_tile_end= current_tile.can_connect(open_end, other_tile)
                    if(other_tile_end is not None):
                        tile_graph.save()
                        tile_graph.add_edge(current_tile, open_end, other_tile, other_tile_end)
                        if(is_tile_graph_valid(other_tile, self.label_mapping, self.k_neighborhood, self.wl_iterations)):
                            found=True
                        else:
                            tile_graph.restore()
                        
                if found:
                    continue
            
            # If no connection found or probability failed, create a new tile of the wanted type
            possible_connections = self.auxiliary_structure[current_tile.original_tile][open_end]
            new_tile_choice = random.choice(possible_connections)
            new_tile_instance = new_tile_choice.clone_with_unique_id(unique_id= count_generated_tiles+1)

            tile_graph.save()
            tile_graph.add_tile(new_tile_instance)

            # Connect the current tile's open end to the new tile
            new_tile_open_end = new_tile_instance.get_open_end(current_tile.tile_label)
            if new_tile_open_end is None:
                raise ValueError("Matching OpenEnd not found in the new tile instance.")

            tile_graph.add_edge(current_tile, open_end, new_tile_instance, new_tile_open_end)
            if(not is_tile_graph_valid(new_tile_instance, self.label_mapping, self.k_neighborhood, self.wl_iterations)):
                tile_graph.restore()
                print("No match:", count, " Tile:", current_tile.tile_label, " Tried to connect to a new:", new_tile_instance.tile_label)
                count += 1
                if count > 10:
                    break

            

        return tile_graph.get_all_tiles()

    def generate_graph(self, default_probability_of_closing=0.5, size=None):
        """
        Generate a new graph using PGG with the tilset induced from the input Graph 'self.graph' with which 'self' was instantiated.
        """
        generated_tiles = self._procedural_graph_generation(p=default_probability_of_closing, size=size)
        return generated_tiles


