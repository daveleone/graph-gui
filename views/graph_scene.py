from PyQt6.QtWidgets import QGraphicsScene, QMenu, QColorDialog, QInputDialog, QGraphicsView, QMessageBox, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPen
from models.node import Node
from models.edge import Edge

class GraphScene(QGraphicsScene):
    graphModified = pyqtSignal()  # New signal for graph modifications
    
    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.node_counter = 0
        self.selected_node = None
        self.mode = None 
        self.metrics_callback = None
        self.last_pan_pos = None
        self.moving_node = None  # Track the node being moved
        self.menu_open = False
        
    def set_metrics_callback(self, callback):
        self.metrics_callback = callback
        
    def update_metrics(self):
        if self.metrics_callback:
            self.metrics_callback()
        self.graphModified.emit()  # Emit signal when graph is modified

    def add_node(self, pos):
        node_id = f"n{self.node_counter}"
        self.node_counter += 1
        node = Node(node_id, pos)
        
        # Create visual representation
        ellipse = self.addEllipse(pos.x() - node.radius, pos.y() - node.radius, node.radius * 2, node.radius * 2, 
                                QPen(Qt.GlobalColor.black), 
                                node.color)
        text = self.addText(node_id)
        text.setPos(pos.x() - node.radius / 2, pos.y() - node.radius / 2)
        text.setZValue(2)
        
        # Store node
        node.graphics_item = ellipse
        node.text_item = text
        self.nodes[node_id] = node
        
        self.update_metrics()
        return node

    def delete_node(self, node):
        # Remove all edges connected to this node
        edges_to_remove = node.edges.copy()
        for edge in edges_to_remove:
            self.delete_edge(edge)
        
        # Remove visual items
        self.removeItem(node.graphics_item)
        self.removeItem(node.text_item)
        
        # Remove from nodes dictionary
        del self.nodes[node.id]
        
        self.menu_open = False
        self.update_metrics()

    def add_edge(self, source_node, target_node):
        if source_node != target_node:
            line = self.addLine(source_node.pos.x(), source_node.pos.y(),
                            target_node.pos.x(), target_node.pos.y())
            
            edge = Edge(source_node, target_node)
            edge.graphics_item = line
            source_node.edges.append(edge)
            target_node.edges.append(edge)
            
            self.update_metrics()
            return edge

    def delete_edge(self, edge):
        # Remove edge from both nodes
        if edge in edge.source.edges:
            edge.source.edges.remove(edge)
        if edge in edge.target.edges:
            edge.target.edges.remove(edge)
        
        # Remove visual item
        self.removeItem(edge.graphics_item)
        
        self.update_metrics()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.handle_right_click(event)
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            if self.menu_open:
                self.menu_open = False
                return

            pos = event.scenePos()
            
            if self.mode == "pan":
                self.last_pan_pos = pos
                for view in self.views():
                    view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            elif self.mode == "add_node":
                self.add_node(pos)
            elif self.mode == "add_edge":
                self.handle_edge_creation(pos)
            elif self.mode == "move_node":
                # Check if we clicked on a node
                items = self.items(pos)
                for item in items:
                    if isinstance(item, type(self.addEllipse(0,0,0,0))):
                        self.moving_node = self.find_node_by_item(item)
                        break
                
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == "pan":
                self.last_pan_pos = None
                for view in self.views():
                    view.setDragMode(QGraphicsView.DragMode.NoDrag)
            elif self.mode == "move_node":
                self.moving_node = None
        
    def mouseMoveEvent(self, event):
        if self.mode == "pan" and self.last_pan_pos is not None:
            pos = event.scenePos()
            delta = pos - self.last_pan_pos
            for view in self.views():
                view.horizontalScrollBar().setValue(
                    view.horizontalScrollBar().value() - delta.x())
                view.verticalScrollBar().setValue(
                    view.verticalScrollBar().value() - delta.y())
            self.last_pan_pos = pos
        elif self.mode == "move_node" and self.moving_node is not None:
            # Update node position
            pos = event.scenePos()
            self.moving_node.pos = pos
            self.moving_node.graphics_item.setRect(pos.x() - self.moving_node.radius, pos.y() - self.moving_node.radius, self.moving_node.radius * 2, self.moving_node.radius * 2)
            self.moving_node.text_item.setPos(pos.x() - self.moving_node.radius / 2, pos.y() - self.moving_node.radius / 2)
            
            # Update connected edges
            for edge in self.moving_node.edges:
                if edge.source == self.moving_node:
                    edge.graphics_item.setLine(pos.x(), pos.y(),
                                            edge.target.pos.x(), edge.target.pos.y())
                else:
                    edge.graphics_item.setLine(edge.source.pos.x(), edge.source.pos.y(),
                                            pos.x(), pos.y())
            self.update_metrics()

    def handle_right_click(self, event):
        pos = event.scenePos()
        items = self.items(pos)
        
        menu = QMenu()
        has_items = False
        
        for item in items:
            if isinstance(item, type(self.addEllipse(0,0,0,0))):
                has_items = True
                node = self.find_node_by_item(item)
                if node:
                    color_action = menu.addAction("Change Node Color")
                    color_action.triggered.connect(lambda: self.change_node_color(node))
                    
                    label_color_action = menu.addAction("Change Label Color")
                    label_color_action.triggered.connect(lambda: self.change_label_color(node))

                    node_size_action = menu.addAction("Change Node Size")
                    node_size_action.triggered.connect(lambda: self.change_node_size(node))

                    delete_action = menu.addAction("Delete Node")
                    delete_action.triggered.connect(lambda: self.delete_node(node))
                    
                    break
            
            elif isinstance(item, type(self.addLine(0,0,0,0))):
                has_items = True
                edge = self.find_edge_by_item(item)
                if edge:
                    delete_action = menu.addAction("Delete Edge")
                    delete_action.triggered.connect(lambda: self.delete_edge(edge))
                    
                    color_action = menu.addAction("Change Edge Color")
                    color_action.triggered.connect(lambda: self.change_edge_color(edge))

                    edge_thickness_action = menu.addAction("Change Edge Thickness")
                    edge_thickness_action.triggered.connect(lambda: self.change_edge_thickness(edge))
                    
                    break 
        
        if not has_items:
           return 
        
        if not menu.isEmpty():
            self.menu_open = True
            menu.exec(event.screenPos())


    def change_node_color(self, node):
        color = QColorDialog.getColor()
        if color.isValid():
            node.color = color
            node.graphics_item.setBrush(color)
            self.menu_open = False
            self.update_metrics()
    
    def change_edge_color(self, edge):
        color = QColorDialog.getColor()
        if color.isValid():
            edge.graphics_item.setPen(QPen(color))
            self.menu_open = False
            self.update_metrics()
    
    def change_label_color(self, node):
        color = QColorDialog.getColor()
        if color.isValid():
            node.text_item.setDefaultTextColor(color)
            self.menu_open = False
            self.update_metrics()

    def change_edge_thickness(self, edge):
        value, ok = QInputDialog.getInt(None, "Change Edge Thickness", "Enter new thickness:", min=1, max=10)
        if ok:
            pen = edge.graphics_item.pen()
            pen.setWidth(value)
            edge.graphics_item.setPen(pen)
            self.menu_open = False
            self.update_metrics()

    def change_node_size(self, node):
        radius, ok = QInputDialog.getInt(
            None,
            "Change Node Size",
            "Enter new node size (radius in pixels):",
            min=20,
            max=100,
            value=20
        )

        if ok:
            node.radius = radius
            x = node.pos.x() - radius
            y = node.pos.y() - radius
            width = height = 2 * radius

            node.graphics_item.setRect(x, y, width, height)

            font = node.text_item.font()
            font.setPointSize(int(radius / 2))
            node.text_item.setFont(font)

            text_width = node.text_item.boundingRect().width()  # Larghezza del testo
            text_height = node.text_item.boundingRect().height()  # Altezza del testo
            text_x = node.pos.x() - text_width / 2  # Centra orizzontalmente
            text_y = node.pos.y() - text_height / 2  # Centra verticalmente

            # Aggiorna la posizione dell'etichetta
            node.text_item.setPos(text_x, text_y)

            self.menu_open = False
            self.update_metrics()

    def handle_edge_creation(self, pos):
        items = self.items(pos)
        for item in items:
            if isinstance(item, type(self.addEllipse(0,0,0,0))):
                clicked_node = self.find_node_by_item(item)
                if clicked_node:
                    if self.selected_node is None:
                        self.selected_node = clicked_node
                    else:
                        if clicked_node != self.selected_node:
                            self.add_edge(self.selected_node, clicked_node)
                        self.selected_node = None

    def find_node_by_item(self, item):
        for node in self.nodes.values():
            if node.graphics_item == item:
                return node
        return None

    def find_edge_by_item(self, item):
        for node in self.nodes.values():
            for edge in node.edges:
                if edge.graphics_item == item:
                    return edge
        return None


    def show_color_dialog(self, element_type):
        if element_type == "nodes" or element_type == "labels":
            has_elements = len(self.nodes) > 0
            warning_message = "There are no nodes in the graph. Please add nodes before changing their color."
        elif element_type == "edges":
            has_elements = any(len(node.edges) > 0 for node in self.nodes.values())
            warning_message = "There are no edges in the graph. Please add edges before changing their color."

        if not has_elements:
            QMessageBox.warning(
                None,
                "Error",
                warning_message 
            )
            return

        color = QColorDialog.getColor()
        if color.isValid():
            if element_type == "nodes":
                self.change_nodes_color(color)
            elif element_type == "edges":
                self.change_edges_color(color)
            elif element_type == "labels":
                self.change_labels_color(color)

    def show_thickness_dialog(self):
        edge_count = sum(len(node.edges) for node in self.nodes.values()) // 2  # Conta gli edge
        if edge_count == 0:
            QMessageBox.warning(
                None,
                "Error",
                f"There are no edges in the graph. Please add edges before changing their thickness."
            )
            return

        value, ok = QInputDialog.getInt(None, "Change Edge Thickness", "Enter new thickness:", min=1, max=10)
        if ok:
            self.change_edges_thickness(value) 

    def show_node_size_dialog(self):
        if not self.nodes:
            QMessageBox.warning(
                None,
                "Error",
                "There are no nodes in the graph. Please add nodes before changing their size."
            )
            return

        value, ok = QInputDialog.getInt(
            None,
            "Change Node Size",
            "Enter new node size (radius in pixels):",
            min=20,
            max=100,
            value=20
        )

        if ok:
            self.change_nodes_size(value)


    def change_nodes_color(self, color):
        for node in self.nodes.values():
            node.color = color
            node.graphics_item.setBrush(color)
        self.menu_open = False
        self.update_metrics()

    def change_edges_color(self, color):
        for node in self.nodes.values():
            for edge in node.edges:
                edge.graphics_item.setPen(QPen(color))
        self.menu_open = False
        self.update_metrics()

    def change_labels_color(self, color):
        for node in self.nodes.values():
            node.text_item.setDefaultTextColor(color)
        self.menu_open = False
        self.update_metrics()

    def change_edges_thickness(self, value):
        for node in self.nodes.values():
            for edge in node.edges:
                pen = edge.graphics_item.pen()
                pen.setWidth(value)
                edge.graphics_item.setPen(pen)
        self.menu_open = False
        self.update_metrics()

    def change_nodes_size(self, radius):
        for node in self.nodes.values():
            node.radius = radius
            x = node.pos.x() - radius
            y = node.pos.y() - radius
            width = height = 2 * radius

            node.graphics_item.setRect(x, y, width, height)

            font = node.text_item.font()
            font.setPointSize(int(radius / 2))
            node.text_item.setFont(font)

            text_width = node.text_item.boundingRect().width()
            text_height = node.text_item.boundingRect().height()
            text_x = node.pos.x() - text_width / 2
            text_y = node.pos.y() - text_height / 2

            node.text_item.setPos(text_x, text_y)

        self.menu_open = False
        self.update_metrics()

    def clear_all(self):
        self.clear()
        self.nodes.clear()
        self.node_counter = 0
        self.selected_node = None
        self.update_metrics() 