def export_networkx(scene):
    code = "import networkx as nx\n\n"
    code += "G = nx.Graph()\n\n"
    
    for node in scene.nodes.values():
        code += f"G.add_node('{node.id}')\n"
    
    added_edges = set()
    for node in scene.nodes.values():
        for edge in node.edges:
            edge_tuple = tuple(sorted([edge.source.id, edge.target.id]))
            if edge_tuple not in added_edges:
                code += f"G.add_edge('{edge.source.id}', '{edge.target.id}')\n"
                added_edges.add(edge_tuple)
    
    code += "\n# Optional: If you want to preserve the layout\n"
    code += "pos = {\n"
    for node in scene.nodes.values():
        code += f"    '{node.id}': ({node.pos.x()}, {node.pos.y()}),\n"
    code += "}\n"
    code += "nx.draw(G, pos=pos, with_labels=True)\n"
    
    return code

def export_igraph(scene):
    code = "import igraph as ig\n\n"
    code += "g = ig.Graph()\n\n"
    
    code += f"g.add_vertices({len(scene.nodes)})\n"
    code += "g.vs['name'] = " + str([node.id for node in scene.nodes.values()]) + "\n"
    
    edges = []
    added_edges = set()
    for node in scene.nodes.values():
        for edge in node.edges:
            edge_tuple = tuple(sorted([edge.source.id, edge.target.id]))
            if edge_tuple not in added_edges:
                edges.append((edge.source.id, edge.target.id))
                added_edges.add(edge_tuple)
    
    code += "edges = " + str(edges) + "\n"
    code += "g.add_edges(edges)\n\n"

    code += "# Store node positions as a layout\n"
    code += "layout = [\n"
    for node in scene.nodes.values():
        code += f"    ({node.pos.x()}, {node.pos.y()}),\n"
    code += "]\n"
    
    return code

def export_pyvis(scene):
    code = "from pyvis.network import Network\n\n"
    code += "net = Network()\n\n"
    
    for node in scene.nodes.values():
        code += f"net.add_node('{node.id}', x={node.pos.x()}, y={node.pos.y()})\n"
    
    added_edges = set()
    for node in scene.nodes.values():
        for edge in node.edges:
            edge_tuple = tuple(sorted([edge.source.id, edge.target.id]))
            if edge_tuple not in added_edges:
                code += f"net.add_edge('{edge.source.id}', '{edge.target.id}')\n"
                added_edges.add(edge_tuple)
    
    code += "\nnet.show('graph.html')\n"
    return code

def export_graphtool(scene):
    code = "from graph_tool.all import *\n\n"
    code += "g = Graph()\n"
    code += "name = g.new_vertex_property('string')\n"
    code += "pos = g.new_vertex_property('vector<double>')\n\n"
    
    code += "vertices = {}\n"
    for node in scene.nodes.values():
        code += f"v = g.add_vertex()\n"
        code += f"name[v] = '{node.id}'\n"
        code += f"pos[v] = [{node.pos.x()}, {node.pos.y()}]\n"
        code += f"vertices['{node.id}'] = v\n"
    
    added_edges = set()
    for node in scene.nodes.values():
        for edge in node.edges:
            edge_tuple = tuple(sorted([edge.source.id, edge.target.id]))
            if edge_tuple not in added_edges:
                code += f"g.add_edge(vertices['{edge.source.id}'], vertices['{edge.target.id}'])\n"
                added_edges.add(edge_tuple)
    
    return code

def export_dgl(scene):
    code = "import dgl\n"
    code += "import torch\n\n"
    
    code += "# Create node ID mappings\n"
    code += "node_mapping = {\n"
    for i, node in enumerate(scene.nodes.values()):
        code += f"    '{node.id}': {i},\n"
    code += "}\n\n"
    
    src_nodes = []
    dst_nodes = []
    added_edges = set()
    for node in scene.nodes.values():
        for edge in node.edges:
            edge_tuple = tuple(sorted([edge.source.id, edge.target.id]))
            if edge_tuple not in added_edges:
                src_nodes.append(f"node_mapping['{edge.source.id}']")
                dst_nodes.append(f"node_mapping['{edge.target.id}']")
                added_edges.add(edge_tuple)
    
    code += "# Create edge lists\n"
    code += f"src_nodes = torch.tensor([{', '.join(src_nodes)}])\n"
    code += f"dst_nodes = torch.tensor([{', '.join(dst_nodes)}])\n\n"
    
    code += "# Create DGL graph\n"
    code += "g = dgl.graph((src_nodes, dst_nodes))\n"
    
    return code

def export_snap(scene):
    code = "import snap\n\n"
    code += "# Create an undirected graph\n"
    code += "G = snap.TNGraph.New()\n\n"
    
    code += "# Add nodes\n"
    for node in scene.nodes.values():
        code += f"G.AddNode(int('{node.id}'[1:]))\n"
    
    code += "\n# Add edges\n"
    added_edges = set()
    for node in scene.nodes.values():
        for edge in node.edges:
            edge_tuple = tuple(sorted([edge.source.id, edge.target.id]))
            if edge_tuple not in added_edges:
                code += f"G.AddEdge(int('{edge.source.id}'[1:]), int('{edge.target.id}'[1:]))\n"
                added_edges.add(edge_tuple)
    
    return code

def export_pygraphviz(scene):
    code = "import pygraphviz as pgv\n\n"
    code += "# Create a new undirected graph\n"
    code += "G = pgv.AGraph(strict=False, directed=False)\n\n"
    
    code += "# Add nodes with their positions\n"
    for node in scene.nodes.values():
        pos = f"{node.pos.x()},{node.pos.y()}!"
        code += f"G.add_node('{node.id}', pos='{pos}')\n"
    
    code += "\n# Add edges\n"
    added_edges = set()
    for node in scene.nodes.values():
        for edge in node.edges:
            edge_tuple = tuple(sorted([edge.source.id, edge.target.id]))
            if edge_tuple not in added_edges:
                code += f"G.add_edge('{edge.source.id}', '{edge.target.id}')\n"
                added_edges.add(edge_tuple)
    
    return code 