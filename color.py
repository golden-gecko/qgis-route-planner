import secrets

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
        names = list(Color.colors.keys())
        weights = [1 / (count + 1) for count in Color.colors.values()]

        scale = 10 ** 6
        int_weights = [max(1, int(w * scale)) for w in weights]
        total = sum(int_weights)
        r = secrets.randbelow(total)

        cum = 0
        idx = 0
        for i, w in enumerate(int_weights):
            cum += w
            if r < cum:
                idx = i
                break

        color = names[idx]
        Color.colors[color] += 1
        return QColor(color)
