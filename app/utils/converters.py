import json


def to_path_map(node_names):
    dict = {}
    for name in node_names:
        dict[name] = name
    return dict


def directory_tree_str_to_json(directory_tree):
    lines = directory_tree.strip().split("\n")
    result = {}
    path = []

    for line in lines:
        level = line.count("│") + line.count("├")
        name = line.split("─")[-1].strip()

        while len(path) >= level:
            path.pop()

        if (
            name.count('.') == 1 and not name.startswith('.') and name.split('.')[-1].isalnum()
            or name.startswith('.') and name in {'.env', '.env.example', '.DS_Store', '.gitignore', '.dockerignore', '.editorconfig', '.npmrc', '.babelrc', '.eslintrc'}
            or name in {'Dockerfile', 'dockerfile', 'Makefile', 'README', 'LICENSE', 'CHANGELOG', 'Procfile', 'Gemfile', 'Rakefile'}
        ):
            current = result
            for dir in path:
                current = current.setdefault(dir, {})
            current[name] = False
        else:  # It's a directory
            path.append(name)

    return json.dumps(result)
