from os.path import split

from PIL import Image

loadingBar = False
# fileName = "Screenshot 2024-12-22 150258.png"
fileName = "cat-close-up-of-side-profile"
processedFileName = "cat-close-up-of-side-profile"


def listToStr(listIn):
    strOut = ""
    for c in listIn:
        strOut += c
    return strOut


class ImageProcessor:
    def __init__(self):
        self.image = Image.open(fr"images\raw\{fileName}.png", 'r')
        self.rawPixels = self.image.load()  # object with tuple data of all pixels
        self.imageSize = self.image.size  # X and Y size of image
        self.blkSize = 50  # side length of blocks
        self.processedPixels = []
        self.finalBlockWidth = self.imageSize[0] % self.blkSize  # actual width of rightmost block on every row
        self.finalRowHeight = self.imageSize[1] % self.blkSize  # actual height of every block on the bottom row
        if self.finalBlockWidth == 0:
            self.finalBlockWidth = self.blkSize
        if self.finalRowHeight == 0:
            self.finalRowHeight = self.blkSize

    def getColors(self):
        """
        calculates average colors in each block.
        does not store pixel data, lowering execution time.
        """
        progress = 0
        totalPixels = self.imageSize[0] * self.imageSize[1]
        loadingDisplay = 0
        for y in range(self.imageSize[1]):
            col = -1
            for x in range(self.imageSize[0]):
                if (x % self.blkSize) == 0:
                    col += 1
                    if (y % self.blkSize) == 0:
                        if x == 0:  # every new row of blocks
                            if y != 0:  # no such previous row in the first iteration
                                self.__averageColors(self.blkSize)
                            self.processedPixels.append([])
                        self.processedPixels[-1].append([0, 0, 0])  # every new block
                currentPixel = self.rawPixels[x, y]
                for po in range(3):
                    self.processedPixels[-1][col][po] += currentPixel[po]

                if loadingBar:  # ~25% performance impact. WIP due to floating point error.
                    print(progress * 10 / totalPixels)
                    progress += 1
                    if ((progress * 10 / totalPixels) % 1) == 0:
                        loadingDisplay += 10
                        print(f"{loadingDisplay}%")

        self.__averageColors(self.finalRowHeight)  # average colors of blocks for the final row, given its height

    def __averageColors(self, rowHeight):
        """
        averages out colors of a row of blocks.
        intended to be used only inside getColors.
        takes into account the actual size of each block within the image's boundary only.
        """
        prevRow = self.processedPixels[-1]
        iSize = len(prevRow) - 1
        for b in range(iSize):
            for c in range(3):
                prevRow[b][c] /= rowHeight * self.blkSize
        for c in range(3):
            prevRow[iSize][c] /= rowHeight * self.finalBlockWidth
        self.processedPixels[-1] = prevRow

    def saveProcessedPixels(self):
        pixelDatFile = open(fr"images\processed\{fileName}", 'w')
        pixelDatFile.writelines(f"{self.imageSize[0]} {self.imageSize[1]}---")
        pixelDatFile.writelines(f"{self.blkSize}---")
        for row in self.processedPixels:
            row = list(str(row))
            row.pop(0)
            row.pop(-1)
            row = listToStr(row)
            row = row.replace(' ', '')
            row = row.replace("],", '-')
            row = row.replace('[', '')
            pixelDatFile.writelines(f"{row}")
        pixelDatFile.close()
        print(fr"Saved in images\processed\{fileName}")

    def loadPixels(self):
        pixelDatFile = open(fr'images\processed\{processedFileName}', 'r')
        pixelDat = pixelDatFile.readline().split("---")
        pixelDatFile.close()

        imageSize = ["", ""]
        xy = 0
        for n in pixelDat[0]:
            if n == ' ':
                xy = 1
                continue
            imageSize[xy] += n
        self.imageSize = (int(imageSize[0]), int(imageSize[1]))

        self.blkSize = int(pixelDat[1])

        rows = pixelDat[2].split(']')
        rows.pop(-1)
        for i in range(len(rows)):
            rows[i] = rows[i].split('-')
            for j in range(len(rows[i])):
                rows[i][j] = rows[i][j].split(',')
                for k in range(len(rows[i][j])):
                    rows[i][j][k] = float(rows[i][j][k])
        self.processedPixels = rows

        self.finalBlockWidth = self.imageSize[0] % self.blkSize  # actual width of rightmost block on every row
        self.finalRowHeight = self.imageSize[1] % self.blkSize  # actual height of every block on the bottom row

        print(fr"Loaded from images\processed\{processedFileName}")

    def pixelateResult(self):
        result = Image.new("RGB", self.imageSize)
        self.rawPixels = result.load()

        row = -1
        for y in range(self.imageSize[1]):
            col = -1
            for x in range(self.imageSize[0]):
                if (x % self.blkSize) == 0:
                    col += 1
                    if (y % self.blkSize) == 0:
                        if x == 0:  # every new row of blocks
                            row += 1
                        # every new block
                pixelColor = self.processedPixels[row][col]
                self.rawPixels[x, y] = (int(pixelColor[0]), int(pixelColor[1]), int(pixelColor[2]))

        result.save(fr"images\result\{processedFileName}.png")

        print(fr"Saved result in images\result\{processedFileName}.png")


myImage = ImageProcessor()
myImage.getColors()
myImage.saveProcessedPixels()
myImage.loadPixels()
myImage.pixelateResult()
