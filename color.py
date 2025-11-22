import random

from qgis.PyQt.QtGui import QColor


class Color:
    @staticmethod
    def random() -> QColor:
        colors = [
            'black',
            'blue',
            'cyan',
            'gray',
            'green',
            'magenta',
            'red',
        ]

        return QColor(random.choice(colors))
