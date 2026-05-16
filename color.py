import random

from qgis.PyQt.QtGui import QColor


class Color:
    colors = [
        'blue',
        'cyan',
        'green',
        'magenta',
        'red',
        'yellow',
    ]

    @staticmethod
    def random() -> QColor:
        return QColor(random.choice(Color.colors))
