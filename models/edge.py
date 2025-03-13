from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen

class Edge:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.graphics_item = None 
        self.color = QColor(Qt.GlobalColor.black)