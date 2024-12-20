from PIL import Image


class ImageProcessor:
    def __init__(self, imagePath):
        self.image = Image.open(imagePath)
        self.rawPixels = self.image.load()  # object with tuple data of all pixels
        self.imageSize = self.image.size  # X and Y size of image
        self.blkSize = 100  # side length of blocks
        self.processedPixels = []

    def getColors(self):
        """
        calculates average colors in each block.
        does not store pixel data, lowering execution time.
        """
        for y in range(self.imageSize[1]):
            col = -1
            for x in range(self.imageSize[0]):
                if (x % self.blkSize) == 0:
                    col += 1
                    if (y % self.blkSize) == 0:
                        if x == 0:  # every new row of blocks
                            if y != 0:  # no previous row in the first iteration
                                self.__averageColors()
                            self.processedPixels.append([])
                        self.processedPixels[-1].append([0, 0, 0])  # every new block
                currentPixel = self.rawPixels[x, y]
                for po in range(3):
                    self.processedPixels[-1][col][po] += currentPixel[po]
        self.__averageColors()  # average colors of blocks for the final row
        print(self.imageSize)
        print(len(self.processedPixels[-1]), len(self.processedPixels))
        print(self.processedPixels)

    def __averageColors(self):
        prevRow = self.processedPixels[-1]
        for b in range(len(prevRow)):
            for c in range(3):
                prevRow[b][c] /= self.blkSize ** 2
        self.processedPixels[-1] = prevRow


myImage = ImageProcessor(r"images\raw\IMG_2408.jpeg")
myImage.getColors()
