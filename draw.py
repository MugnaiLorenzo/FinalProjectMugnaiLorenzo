import matplotlib.pyplot as plt
import matplotlib.text as text
import numpy as np


class Draw:
    def __init__(self, x1, x2, matrix):
        fig, ax = plt.subplots()
        labelx = []
        labely = []
        i = 0
        for m in matrix:
            labelx.append(text.Text(i, 0, m[1]))
            i = i + 1
        self.x1 = np.array(x1)
        self.x2 = np.array(x2)
        plt.plot(self.x1, marker='*')
        plt.plot(self.x2, marker='*')
        for x in x1:
            if round(x, 1) not in labely:
                labely.append(round(x, 1))
        for x in x2:
            if round(x, 1) not in labely:
                labely.append(round(x, 1))
        ax.set_yticks(labely)
        ax.set_xticks(range(len(labelx)))
        ax.set_xticklabels(labelx)
        plt.savefig("draw.png")
