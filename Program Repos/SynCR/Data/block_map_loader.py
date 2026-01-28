import json

def load_block_map(file_path="Data/block_map.json"):
    """
    Loads the block map from a JSON file.
    """
    with open(file_path, "r") as file:
        block_map = json.load(file)
    return block_map
