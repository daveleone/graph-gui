<p align="center"><a href="" target="_blank"><img src="https://raw.githubusercontent.com/daveleone/graph-gui/refs/heads/main/resources/icon.svg" width="120" alt="Graph Visualizer Logo"></a></p>

# Graph Visualizer

A Python-based application for graphical representation and manipulation of graphs.

## Overview

**Graph Visualizer** aims to provide an interactive graphical user interface for visualizing and working with graphs. Whether you're studying graph theory or teaching, this tool offers an accessible way to create and explore graph structures. 

## Features

- Visual creation and editing of nodes and edges
- Interactive graph visualization
- Support for basic graph algorithms
- Export and import of graph data

## Supported Libraries

Graph Visualizer supports multiple Python graph libraries for importing graph data and, where applicable, exporting the generated code.  
This allows users to explore graphs within the application while maintaining compatibility with widely used graph frameworks.  

Currently supported libraries include:

- **NetworkX**  
- **Graph-tool**
- **igraph**
- **PyVis**
- **PyGraphviz**
- **DGL (Deep Graph Library)** 
- **SNAP**

Future versions may extend the range of supported libraries and improve export functionality.

### Future Developments

While the current implementation of metrics relies on **NetworkX**, future versions will focus on integrating more efficient algorithms and extending support for advanced computations across different libraries.

## Getting Started

### Prerequisites

- Python 3.x

### Installation

Clone the repository:
```bash
git clone https://github.com/daveleone/graph-gui.git
cd graph-gui
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

Run the main application:
```bash
python main.py
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests if you have suggestions or improvements.
