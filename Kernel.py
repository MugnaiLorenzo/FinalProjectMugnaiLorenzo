import numpy as np


class Kernel:
    def __init__(self):
        self.identity = np.matrix([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
        self.ridge = np.matrix([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
        self.edgeDetection = np.matrix([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        self.sharpen = np.matrix([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        self.boxBlur = 1 / 9 * np.matrix([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        self.gaussianBlur3 = 1 / 16 * np.matrix([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
        self.gaussianBlur5 = 1 / 256 * np.matrix(
            [[1, 4, 6, 4, 1], [4, 16, 24, 16, 4], [6, 24, 36, 24, 6], [4, 16, 24, 16, 4], [1, 4, 6, 4, 1]])
        self.unsharpMasking = -1 / 256 * np.matrix(
            [[1, 4, 6, 4, 1], [4, 16, 24, 16, 4], [6, 24, -476, 24, 6], [4, 16, 24, 16, 4], [1, 4, 6, 4, 1]])

    def getIdentity(self):
        return self.identity

    def getRidge(self):
        return self.ridge

    def getEdgeDetection(self):
        return self.edgeDetection

    def getSharpen(self):
        return self.sharpen

    def getBoxBlur(self):
        return self.boxBlur

    def getGaussianBlur3(self):
        return self.gaussianBlur3

    def getGaussianBlur5(self):
        return self.gaussianBlur5

    def getUnsharpMasking(self):
        return self.unsharpMasking

    # def getMatrix(self):
    #     return [[self.getIdentity(), "_id"], [self.getRidge(), "_rid"], [self.getEdgeDetection(), "_edgDet"],
    #             [self.getSharpen(), "_shar"], [self.getBoxBlur(), "_boxBlur"], [self.getGaussianBlur3(), "gaussian3"],
    #             [self.getGaussianBlur5(), "gaussian5"], [self.getUnsharpMasking(), "_unsharpMask"]]

    def getMatrix(self):
        return [[self.getGaussianBlur3(), "gaussian3"], [self.getBoxBlur(), "_boxBlur"],
                [self.getGaussianBlur5(), "gaussian5"], [self.getUnsharpMasking(), "_unsharpMask"]]
