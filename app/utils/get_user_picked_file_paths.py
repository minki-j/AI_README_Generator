from typing import List

def get_user_picked_file_paths(directory_tree_dict, current_path="") -> List[str]:
    true_paths = []
    for key, value in directory_tree_dict.items():
        full_path = f"{current_path}/{key}" if current_path else key
        if isinstance(value, dict):
            true_paths.extend(get_user_picked_file_paths(value, full_path))
        elif value:
            true_paths.append(full_path)
    return true_paths
