import os
import math
from PIL import Image

loadingBar = True
fileExt = ""

while True:
    try:
        fileList = ""
        for p in os.listdir(r"images\raw"):
            if not p.startswith("blockTextures"):
                fileList += f"{p} | "
        print(f"| {fileList}")
        fileName = input("Enter exact name of one of the files to open: ")
        fileExt = fileName.split('.')[1]
        fileName = fileName.split('.')[0]
        temp = open(fr"images\raw\{fileName}.{fileExt}")
        break
    except FileNotFoundError:
        print("File not found!")

processedFileName = fileName
saveFileName = f"{processedFileName}"
blkDat = []
textureRes = Image.open(r"images\raw\blockTextures\dirt.png").size[0]

while True:
    try:
        blkSize = abs(int(input("Enter block size: ")))
        break
    except ValueError:
        print("Please enter an integer!")


def listToStr(listIn):
    strOut = ""
    for c in listIn:
        strOut += c
    return strOut


def loadBlocks():
    global blkDat
    blkFile = open(r"images/processed/blockTextures.txt", 'r')
    blkDat = blkFile.readlines()
    for i in range(len(blkDat)):
        blkDat[i] = blkDat[i].replace("\n", '')
        blkDat[i] = blkDat[i].split("--")
        blkDat[i][1] = blkDat[i][1].replace('[', '')
        blkDat[i][1] = blkDat[i][1].replace(']', '')
        blkDat[i][1] = blkDat[i][1].split(', ')
        for c in range(3):
            blkDat[i][1][c] = int(blkDat[i][1][c])


def getClosestBlockColor(color):
    minDiff = float("inf")
    minColIdx = -1
    for c in range(len(blkDat)):
        colDiff = abs(color[0] - blkDat[c][1][0]) + abs(color[1] - blkDat[c][1][1]) + abs(color[2] - blkDat[c][1][2])
        if colDiff < minDiff:
            minDiff = colDiff
            minColIdx = c
    return blkDat[minColIdx]


class ImageProcessor:
    def __init__(self):
        self.image = Image.open(fr"images\raw\{fileName}.{fileExt}", 'r')
        self.rawPixels = self.image.load()  # object with tuple data of all pixels
        self.imageSize = self.image.size  # X and Y size of image
        self.blkSize = blkSize  # side length of blocks
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
        totalPixels = self.imageSize[0] * self.imageSize[1]
        progressRaw = 0
        progressPercentage = 0
        progress = 0
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
                    if loadingBar:
                        if progress == progressRaw:
                            print(f"{progressPercentage}%")
                            progressPercentage += 10
                            progressRaw += round(totalPixels / 10)
                        progress += 1

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
        row = -1
        scaledSize = (math.ceil(self.imageSize[0] / self.blkSize), math.ceil(self.imageSize[1] / self.blkSize))
        result = Image.new("RGB", scaledSize)
        self.rawPixels = result.load()

        for y in range(scaledSize[1]):
            col = -1
            for x in range(scaledSize[0]):
                col += 1
                if x == 0:  # every new row of blocks
                    row += 1
                pixelColor = self.processedPixels[row][col]
                self.rawPixels[x, y] = (round(float(pixelColor[0])), round(float(pixelColor[1])), round(float(pixelColor[2])))

        result.save(fr"images\result\{processedFileName}.png")
        print(fr"Saved result in images\result\{processedFileName}.png")

    def minecraft(self):
        result = Image.new("RGBA", (textureRes * math.ceil(self.imageSize[0] / self.blkSize), textureRes * math.ceil(self.imageSize[1] / self.blkSize)))
        rawPixels = result.load()
        totalPixels = len(self.processedPixels) * len(self.processedPixels[0])
        progressRaw = 0
        progressPercentage = 0
        progress = 0
        for row in range(len(self.processedPixels)):
            for col in range(len(self.processedPixels[row])):
                nearestBlkDat = getClosestBlockColor(self.processedPixels[row][col])
                blkFile = Image.open(fr"images/raw/blockTextures\{nearestBlkDat[0]}")
                blkFile = blkFile.convert("RGBA")
                blkPixels = blkFile.load()
                for x in range(textureRes):
                    for y in range(textureRes):
                        rawPixels[col * textureRes + x, row * textureRes + y] = blkPixels[x, y]  # pixel color at block position (x, y) here

                if loadingBar:
                    if progress == progressRaw:
                        print(f"{progressPercentage}%")
                        progressPercentage += 10
                        progressRaw += round(totalPixels / 10)
                    progress += 1

        result.save(fr"images\result\{processedFileName}_mc.png")
        print(fr"Saved result in images\result\{processedFileName}_mc.png")


myImage = ImageProcessor()
myImage.getColors()
myImage.saveProcessedPixels()
myImage.loadPixels()
# myImage.pixelateResult()
loadBlocks()
myImage.minecraft()
