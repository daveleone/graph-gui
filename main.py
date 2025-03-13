import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QGraphicsView,
    QGraphicsScene,
    QComboBox,
    QMessageBox,
    QInputDialog,
    QMenu,
    QFileDialog,
    QTextEdit,
    QSplitter,
    QTabWidget,
    QLabel,
    QHBoxLayout,
    QPlainTextEdit,
    QToolButton
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainter, QIcon, QFont

from models import node, edge 
from views.graph_scene import GraphScene
from views.custom_graphics_view import CustomGraphicsView
from widgets.code_editor import CodeEditor
from widgets.metrics_panel import MetricsPanel
from utils import exporters
from utils.code_importer import GraphImporter

class GraphEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Editor")
        self.setGeometry(100, 100, 1200, 800)

        # Set application icon
        self.setWindowIcon(QIcon("resources/icon.png"))

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)

        # Left panel (graph editor)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_add_node = QPushButton("Add Node")
        btn_add_node.clicked.connect(lambda: self.set_mode("add_node"))
        btn_add_edge = QPushButton("Add Edge")
        btn_add_edge.clicked.connect(lambda: self.set_mode("add_edge"))
        btn_move_node = QPushButton("Move Node")
        btn_move_node.clicked.connect(lambda: self.set_mode("move_node"))
        btn_pan = QPushButton("Pan Mode")
        btn_pan.clicked.connect(lambda: self.set_mode("pan"))
        btn_clear = QPushButton("Clear All")
        btn_clear.clicked.connect(self.clear_all)

        btn_layout.addWidget(btn_add_node)
        btn_layout.addWidget(btn_add_edge)
        btn_layout.addWidget(btn_move_node)
        btn_layout.addWidget(btn_pan)
        btn_layout.addWidget(btn_clear)
        left_layout.addLayout(btn_layout)

        # Add tooltip for pan mode
        btn_pan.setToolTip(
            "Click to enter pan mode\nYou can also pan by holding the middle mouse button"
        )
        # Add tooltip for move mode
        btn_move_node.setToolTip(
            "Click to enter move mode\nClick and drag nodes to reposition them"
        )

        # Graphics View
        self.scene = GraphScene()
        self.view = CustomGraphicsView(self.scene)
        left_layout.addWidget(self.view)

        # Connect graph modification signal
        self.scene.graphModified.connect(self.update_code_preview)

        self.main_splitter.addWidget(left_widget)

        # Right panel (code and metrics)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)


        btn_right_layout_change = QHBoxLayout()

        # btn_change_colors = QPushButton("Change Colors")
        # btn_change_colors.clicked.connect(lambda: self.scene.show_color_menu())
        btn_change_colors = QToolButton()
        btn_change_colors.setText("Change Colors")
        btn_change_colors.setFixedWidth(140)

        color_menu = QMenu()
        node_color_action = color_menu.addAction("Change All Nodes Color")
        edge_color_action = color_menu.addAction("Change All Edges Color")
        label_color_action = color_menu.addAction("Change All Labels Color")

        node_color_action.triggered.connect(lambda: self.scene.show_color_dialog("nodes"))
        edge_color_action.triggered.connect(lambda: self.scene.show_color_dialog("edges"))
        label_color_action.triggered.connect(lambda: self.scene.show_color_dialog("labels"))

        btn_change_colors.setMenu(color_menu)
        btn_change_colors.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)


        btn_change_thickness = QPushButton("Change Edges Thickness")
        btn_change_thickness.clicked.connect(lambda: self.scene.show_thickness_dialog())

        btn_change_node_size = QPushButton("Change Nodes Size")
        btn_change_node_size.clicked.connect(lambda: self.scene.show_node_size_dialog())

        btn_right_layout_change.addWidget(btn_change_colors)
        btn_right_layout_change.addWidget(btn_change_thickness)
        btn_right_layout_change.addWidget(btn_change_node_size)

        right_layout.addLayout(btn_right_layout_change) 

        # Export controls
        export_layout = QHBoxLayout()
        self.export_combo = QComboBox()
        self.export_combo.addItems(
            ["NetworkX", "igraph", "PyVis", "Graph-tool", "PyGraphviz", "DGL", "SNAP"]
        )
        self.export_combo.currentTextChanged.connect(self.update_code_preview)

        btn_export_clipboard = QPushButton("Copy to Clipboard")
        btn_export_clipboard.clicked.connect(
            lambda: self.export_graph(to_clipboard=True)
        )
        btn_export_file = QPushButton("Save to File")
        btn_export_file.clicked.connect(lambda: self.export_graph(to_clipboard=False))

        export_layout.addWidget(self.export_combo)
        export_layout.addWidget(btn_export_clipboard)
        export_layout.addWidget(btn_export_file)
        right_layout.addLayout(export_layout)

        # Tabs for code and metrics
        self.tabs = QTabWidget()

        # Code preview tab
        self.code_editor = CodeEditor()
        self.code_editor.codeChanged.connect(self._on_code_changed)
        self.code_editor.importRequested.connect(self._on_import_requested)
        self.code_editor.mode_combo.currentTextChanged.connect(
            self._on_editor_mode_changed
        )
        self.tabs.addTab(self.code_editor, "Code Preview/Import")

        # Metrics tab
        self.metrics_panel = MetricsPanel(self.scene)
        self.tabs.addTab(self.metrics_panel, "Metrics")

        right_layout.addWidget(self.tabs)

        # copyright_label = QLabel(
        #     "© 2025 Davide Leone - Università degli Studi di Bari Aldo Moro"
        # )
        # copyright_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # copyright_label.setStyleSheet("color: gray; font-size: 10px;")
        # right_layout.addWidget(copyright_label)

        self.main_splitter.addWidget(right_widget)

        self.scene.set_metrics_callback(self.metrics_panel.update_metrics)

        self.update_code_preview()

        self.main_splitter.setSizes([700, 500])

    def _on_code_changed(self, code):
        if self.code_editor.mode_combo.currentText() == "Preview":
            if not self.code_editor._updating:
                self.update_code_preview()

    def _on_editor_mode_changed(self, mode):
        if mode == "Preview":
            self.update_code_preview()
            self.export_combo.setEnabled(True)
        else:
            self.export_combo.setEnabled(False)

    def _on_import_requested(self, code):
        try:
            GraphImporter.import_from_code(code, self.scene)
            self.update_code_preview()
            QMessageBox.information(self, "Success", "Graph imported successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Import Error", str(e))
            self.code_editor.mode_combo.setCurrentText("Import")

    def update_code_preview(self):
        library = self.export_combo.currentText()
        if library == "NetworkX":
            code = exporters.export_networkx(self.scene)
        elif library == "igraph":
            code = exporters.export_igraph(self.scene)
        elif library == "PyVis":
            code = exporters.export_pyvis(self.scene)
        elif library == "PyGraphviz":
            code = exporters.export_pygraphviz(self.scene)
        elif library == "Graph-tool":
            code = exporters.export_graphtool(self.scene)
        elif library == "DGL":
            code = exporters.export_dgl(self.scene)
        elif library == "SNAP":
            code = exporters.export_snap(self.scene)

        self.code_editor.setPlainText(code)

    def set_mode(self, mode):
        self.scene.mode = mode
        self.scene.selected_node = None
        if mode == "change_colors":
            self.view.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.view.setCursor(Qt.CursorShape.ArrowCursor)

    def clear_all(self):
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Are you sure you want to clear everything?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.scene.clear_all()
            self.update_code_preview()

    def export_graph(self, to_clipboard=True):
        current_tab = self.tabs.currentWidget()

        if isinstance(current_tab, CodeEditor):
            code = self.code_editor.toPlainText()
            if to_clipboard:
                clipboard = QApplication.clipboard()
                clipboard.setText(code)
                QMessageBox.information(self, "Success", "Code copied to clipboard!")
            else:
                file_name, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Code",
                    f"graph_{self.export_combo.currentText().lower()}.py",
                    "Python files (*.py);;All Files (*.*)",
                )
                if file_name:
                    with open(file_name, "w") as f:
                        f.write(code)
                    QMessageBox.information(
                        self, "Success", f"Code saved to {file_name}"
                    )

        elif isinstance(current_tab, MetricsPanel):
            metrics_text = self.get_metrics_text()
            if to_clipboard:
                clipboard = QApplication.clipboard()
                clipboard.setText(metrics_text)
                QMessageBox.information(self, "Success", "Metrics copied to clipboard!")
            else:
                file_name, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Metrics",
                    "graph_metrics.txt",
                    "Text files (*.txt);;All Files (*.*)",
                )
                if file_name:
                    with open(file_name, "w") as f:
                        f.write(metrics_text)
                    QMessageBox.information(
                        self, "Success", f"Metrics saved to {file_name}"
                    )

    def get_metrics_text(self):
        metrics = []
        metrics.append("Graph Metrics Report")
        metrics.append("===================\n")

        num_nodes = len(self.scene.nodes)
        num_edges = sum(len(node.edges) for node in self.scene.nodes.values()) // 2

        metrics.append(f"Number of nodes: {num_nodes}")
        metrics.append(f"Number of edges: {num_edges}")

        if num_nodes > 1:
            density = (2 * num_edges) / (num_nodes * (num_nodes - 1))
            metrics.append(f"Density: {density:.3f}")

        if num_nodes > 0:
            avg_degree = (2 * num_edges) / num_nodes
            metrics.append(f"Average degree: {avg_degree:.2f}")

        metrics.append("\nNode Degrees:")
        for node_id, node in self.scene.nodes.items():
            degree = len(node.edges)
            metrics.append(f"{node_id}: {degree}")

        return "\n".join(metrics)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphEditor()
    window.show()
    sys.exit(app.exec())
