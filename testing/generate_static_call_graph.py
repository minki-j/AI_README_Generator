import os
from pycg.pycg import CallGraphGenerator
import networkx as nx
import matplotlib.pyplot as plt
from pycg.formats.simple import Simple
from pycg.formats.as_graph import AsGraph
import json

def generate_call_graph(project_path, max_iter=5, operation="call-graph"):
    entry_points = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                entry_points.append(os.path.join(root, file))

    cg = CallGraphGenerator(entry_points, project_path, max_iter, operation)
    cg.analyze()
    return cg  # Return the CallGraphGenerator instance instead of its output

def visualize_call_graph(call_graph, output_file='call_graph.png'):
    G = nx.DiGraph()
    for caller, callees in call_graph.items():
        for callee in callees:
            G.add_edge(caller, callee)

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=200, font_size=8, arrows=True)
    plt.title("Static Call Graph")
    plt.savefig(output_file)
    plt.close()

if __name__ == "__main__":
    project_path = "/Users/minkijung/Documents/2PetProjects/AI_README_Generator/app"
    cg = generate_call_graph(project_path)
    
    # Visualize the call graph
    call_graph = cg.output()  # Get the output for visualization
    visualize_call_graph(call_graph)
    print(f"Call graph generated and saved as 'call_graph.png'")

    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

    with open('call_graph.txt', 'w') as f:
        json.dump(call_graph, f, indent=2, default=set_default)
    print(f"Call graph output saved to 'call_graph.txt'")

    # Use Simple formatter and save to file
    formatter = Simple(cg)  # Pass the CallGraphGenerator instance
    simple_output = formatter.generate()
    with open('simple_call_graph.txt', 'w') as f:
        json.dump(simple_output, f, indent=2)
    print(f"Simple call graph output saved to 'simple_call_graph.txt'")

    # Optionally, use AsGraph formatter and save to file
    as_graph_formatter = AsGraph(cg)  # Pass the CallGraphGenerator instance
    as_graph_output = as_graph_formatter.generate()
    with open('as_graph_call_graph.txt', 'w') as f:
        json.dump(as_graph_output, f, indent=2)
    print(f"AsGraph call graph output saved to 'as_graph_call_graph.txt'")
