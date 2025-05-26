import os
from app.config import UPLOAD_DIR, STORAGE_NODES

def get_node_load(node_name: str) -> int:
    node_path = os.path.join(UPLOAD_DIR, node_name)
    total_size = 0
    for root, dirs, files in os.walk(node_path):
        for f in files:
            try:
                fp = os.path.join(root, f)
                total_size += os.path.getsize(fp)
            except OSError:
                pass
    return total_size

def choose_storage_node() -> str:
    loads = {node: get_node_load(node) for node in STORAGE_NODES}
    chosen_node = min(loads, key=loads.get)
    return chosen_node
