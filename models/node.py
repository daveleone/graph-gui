from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor

class Node:
    def __init__(self, id, pos: QPointF):
        self.id = id
        self.pos = pos
        self.edges = []
        self.graphics_item = None
        self.text_item = None
        self.radius = 20
        self.color = QColor(174, 34, 255)