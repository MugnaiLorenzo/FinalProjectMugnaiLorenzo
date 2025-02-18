import os
import numpy as np
from PIL import Image


class ResizeImage:
    def __init__(self, file_name, ext, matrix):
        self.file_name = file_name
        self.img = Image.open(self.file_name)
        self.w = self.img.size[0]
        self.h = self.img.size[1]
        self.img_t = Image.new(mode="RGB", size=(self.w, self.h))
        self.px = self.img.load()
        self.px_t = self.img_t.load()
        self.matrix = matrix


    def transform(self):
        for i in range(self.w - 1):
            for j in range(self.h - 1):
                self.px_t[i, j] = self.mul(i, j)
        return self.img_t

    def mul(self, i, j):
        x = 0
        y = 0
        z = 0
        s = (np.size(self.matrix, 0) - 1) / 2
        row = np.arange(-(np.size(self.matrix, 0) - 1) / 2, (np.size(self.matrix, 0) - 1) / 2 + 1, 1)
        col = np.arange(-(np.size(self.matrix, 1) - 1) / 2, (np.size(self.matrix, 1) - 1) / 2 + 1, 1)
        for r in row:
            for c in col:
                if i + r in range(self.w - 1) and j + c in range(self.h - 1):
                    x = x + self.px[int(i + r), int(j + c)][0] * self.matrix[int(s + r), int(s + c)]
                    y = y + self.px[int(i + r), int(j + c)][1] * self.matrix[int(s + r), int(s + c)]
                    z = z + self.px[int(i + r), int(j + c)][2] * self.matrix[int(s + r), int(s + c)]
        return int(x), int(y), int(z)
