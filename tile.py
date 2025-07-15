from collections import deque
from graph_labelling import wl_labeling

class Tile:
    def __init__(self, tile_label, original_node_id, open_ends, original_tile=None, set_of_subgraphs=set()):
        self.tile_label= tile_label  # Label of the node
        self.original_node_id= original_node_id #The node_id in the Input graph of this Tile's node
        self.original_tile= original_tile #Reference to the original tile from which this tile has been factored
        self.set_of_subgraphs= set_of_subgraphs # Set of labels of all possible subgraphs of the graph that generated the current's tile label
        self.unique_id= 0 # unique id, but 0 for all "Original" tiles
        self.open_ends= open_ends  # List of neighbors.  open_end=(Label, id) with Label being the label of the neighbor node we're looking for, and id being the nodeId of the neighbor in the original graph.
        self.connections= {}  # Track which open end of this tile connects to which other tile. open_end_tuple -> (other_tile, other_open_end)
        self.list_of_neighbor_labels= [open_end_label for (open_end_label, open_end_id) in open_ends] # List with only the labels of the neighbors that we still haven't connected to. 
        self.list_of_already_connected_to= [] # List of tile unique_ids that this Tile is already connected to
        self.backups= deque() # Queue storing previous versions of this tile.
        

    def connect_open_end(self, open_end_tuple, other_tile, other_open_end_tuple):
        """Connect the current tile's open end 'open_end_tuple', to 'other_tile's 'other_open_end_tuple'."""
        self.connections[open_end_tuple] = (other_tile, other_open_end_tuple)
        self.open_ends.remove(open_end_tuple)
        self.list_of_neighbor_labels.remove(open_end_tuple[0])
        self.list_of_already_connected_to.append(other_tile.unique_id)
        other_tile.connections[other_open_end_tuple] = (self, open_end_tuple)
        other_tile.open_ends.remove(other_open_end_tuple)
        other_tile.list_of_neighbor_labels.remove(other_open_end_tuple[0])
        other_tile.list_of_already_connected_to.append(self.unique_id)
    
    def can_connect(self, open_end, other_tile):
        """ returns the open end from other_tile that corresponds to open_end, or None if it doesn't exist. """
        ret= None
        if (other_tile.tile_label == open_end[0]) and (self.tile_label in other_tile.list_of_neighbor_labels) and (other_tile.unique_id not in self.list_of_already_connected_to):
            for other_tile_end in other_tile.open_ends:
                if(other_tile_end[0]==self.tile_label):
                    ret= other_tile_end

        return ret

    def get_open_end(self, label):
        """ returns the first open end in self.open_ends that corresponds to label."""
        ret=None
        for oe in self.open_ends:
            if(oe[0]==label):
                ret= oe
                break

        return ret

    def is_subgraph_of_tile(self, graph, num_iterations, label_mapping):
        """ returns a boolean indicating if 'graph' is a subgraph of this tile"""
        graph_label= wl_labeling(graph, self.unique_id, num_iterations)
        return label_mapping.get(graph_label,0) in self.set_of_subgraphs

    def clone_with_unique_id(self, unique_id):
        """ returns a new instantiation of the current Tile type."""
        cloned_tile = Tile(self.tile_label, self.original_node_id, self.open_ends.copy(), original_tile=self, set_of_subgraphs=self.set_of_subgraphs)
        cloned_tile.unique_id = unique_id
        return cloned_tile

    def save(self):
        self.backups.append((self.open_ends.copy(), self.connections.copy(), self.list_of_neighbor_labels.copy(), self.list_of_already_connected_to.copy()))
    
    def restore(self):
        previous_version= self.backups.pop()
        self.open_ends= previous_version[0]
        self.connections= previous_version[1]
        self.list_of_neighbor_labels= previous_version[2]
        self.list_of_already_connected_to= previous_version[3]


    def __hash__(self):
        return hash((self.tile_label, self.original_node_id))