import random

from qgis.PyQt.QtGui import QColor


class Color:
    colors = {
        'blue': 0,
        'cyan': 0,
        'green': 0,
        'magenta': 0,
        'red': 0,
        'yellow': 0,
    }

    @staticmethod
    def random() -> QColor:
        weights = [1 / (count + 1) for count in Color.colors.values()]
        color = random.choices(list(Color.colors.keys()), weights=weights)[0]

        Color.colors[color] += 1

        return QColor(color)
