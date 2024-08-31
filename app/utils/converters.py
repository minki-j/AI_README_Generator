import json

def to_path_map(node_names):
    dict = {}
    for name in node_names:
        dict[name] = name
    return dict

def directory_tree_str_to_json(directory_tree):
    lines = directory_tree.strip().split('\n')
    result = {}
    path = []

    for line in lines:
        level = line.count('│') + line.count('├') + line.count('└')
        name = line.split('─')[-1].strip()

        while len(path) > level:
            path.pop()

        if '.' in name:  # It's a file
            current = result
            for dir in path:
                current = current.setdefault(dir, {})
            current[name] = False
        else:  # It's a directory
            path.append(name)

    return json.dumps(result)

