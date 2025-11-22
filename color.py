import random

from qgis.PyQt.QtGui import QColor


class Color:
    @staticmethod
    def random() -> QColor:
        colors = [
            'blue',
            'cyan',
            'green',
            'magenta',
            'red',
            'yellow',
        ]

        return QColor(random.choice(colors))
