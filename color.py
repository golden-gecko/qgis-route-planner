import random

from qgis.PyQt.QtGui import QColor


class Color:
    @staticmethod
    def random() -> QColor:
        colors = [
            QColor('black'),
            QColor('blue'),
            QColor('cyan'),
            QColor('gray'),
            QColor('green'),
            QColor('magenta'),
            QColor('red'),
        ]

        return colors[random.randint(0, len(colors) - 1)]
