from collections import deque

class TileGraph:
    def __init__(self):
        self.tiles= [] # all the tiles
        self.open_tiles= [] # tiles with at least one open end
        self.backups= deque()

    def get_open_tiles(self):
        return self.open_tiles

    def get_all_tiles(self):
        return self.tiles
    
    def get_count_generated_tiles(self):
        return len(self.tiles)

    def still_open_tiles(self):
        return len(self.open_tiles)>0

    def add_tile(self, tile): 
        self.tiles.append(tile)
        self.open_tiles.append(tile)

    def add_edge(self, tile_1, open_end_1, tile_2, open_end_2):
        tile_1.connect_open_end(open_end_1, tile_2, open_end_2)

        # Update self.open_tiles
        self.open_tiles = [tile for tile in self.open_tiles if tile.open_ends] # too expensive to run each time, TODO: only check for the concerned tiles: tIle_1 & tile_1

    def save(self):
        self.backups.append((self.tiles.copy(), self.open_tiles.copy()))
        for tile in self.tiles:
            tile.save()

    def restore(self):
        previous_version= self.backups.pop()
        self.tiles= previous_version[0]
        self.open_tiles= previous_version[1]
        for tile in self.tiles:
            tile.restore()