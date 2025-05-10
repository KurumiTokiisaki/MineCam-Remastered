import os
import math
from PIL import Image
import cv2

loadingBar = True
fileExt = ""
mode = "image"
invertColors = False
RGBtoBGR = False

while True:
    try:
        fileList = "| "
        for p in os.listdir(r"images/raw"):
            if not p.startswith("blockTextures"):
                fileList += f"{p} | "
        print(fileList)
        fileName = input("Enter exact name of one of the files to open: ")
        fileExt = fileName.split('.')[1]
        fileName = fileName.split('.')[0]
        temp = open(fr"images/raw/{fileName}.{fileExt}")
        break
    except (FileNotFoundError, IndexError):
        print("File not found!")

if (fileExt == "mp4") or (fileExt == "avi"):
    mode = "video"

processedFileName = fileName
saveFileName = f"{processedFileName}"
blkDat = []
textureRes = Image.open(r"images/raw/blockTextures/dirt.png").size[0]

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
        for rgb in range(3):
            blkDat[i][1][rgb] = int(blkDat[i][1][rgb])


def getClosestBlockColor(color):
    minDiff = float("inf")
    minColIdx = -1
    for rgb in range(len(blkDat)):
        colDiff = abs(color[0] - blkDat[rgb][1][0]) + abs(color[1] - blkDat[rgb][1][1]) + abs(color[2] - blkDat[rgb][1][2])
        if colDiff < minDiff:
            minDiff = colDiff
            minColIdx = rgb
    return blkDat[minColIdx]


class FormattedImage:
    def __init__(self, pixelData):
        self.pixelData = pixelData
        self.size = [len(pixelData), len(pixelData[0])]


class ImageProcessor:
    def __init__(self, imageObj):
        self.image = imageObj
        self.rawPixels = self.image.pixelData  # 2D array with data for all pixels
        self.imageSize = self.image.size  # X and Y size of image
        self.blkSize = blkSize  # side length of blocks
        self.processedPixels = []
        self.finalBlockWidth = self.imageSize[0] % self.blkSize  # actual width of rightmost block on every row
        self.finalRowHeight = self.imageSize[1] % self.blkSize  # actual height of every block on the bottom row
        if self.finalBlockWidth == 0:
            self.finalBlockWidth = self.blkSize
        if self.finalRowHeight == 0:
            self.finalRowHeight = self.blkSize

    def invertColors(self):
        for x in range(len(self.rawPixels)):
            for y in range(len(self.rawPixels[0])):
                for rgb in range(len(self.rawPixels[x][y])):
                    self.rawPixels[x][y][rgb] = 255 - self.rawPixels[x][y][rgb]

    def blockProcess(self):
        self.getColors()
        self.minecraft()

    def getColors(self):
        """
        calculates average colors in each block.
        does not store pixel data, lowering execution time.
        """
        if invertColors:
            self.invertColors()
        if RGBtoBGR:
            for x in range(len(self.rawPixels)):
                for y in range(len(self.rawPixels[0])):
                    self.rawPixels[x][y] = [self.rawPixels[x][y][0], self.rawPixels[x][y][1], self.rawPixels[x][y][2]]  # convert pixel RGB data from tuple to list to make it mutable
                    tempR = self.rawPixels[x][y][0]
                    self.rawPixels[x][y][0] = self.rawPixels[x][y][2]
                    self.rawPixels[x][y][2] = tempR
        totalPixels = self.imageSize[0] * self.imageSize[1]
        progressRaw = 0
        progressPercentage = 1
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
                currentPixel = self.rawPixels[x][y]  # color data of current pixel
                for po in range(3):
                    self.processedPixels[-1][col][po] += currentPixel[po]

                if loadingBar:
                    if progress == progressRaw:
                        print(f"\rColors averaged: {progressPercentage}%", end="")
                        progressPercentage += 1
                        progressRaw += round(totalPixels / 100)
                    progress += 1
        print('')

        self.__averageColors(self.finalRowHeight)  # average colors of blocks for the final row, given its height

    def __averageColors(self, rowHeight):
        """
        averages out colors for a row of blocks.
        intended to be used only inside getColors.
        takes into account the actual size of each block within the image's boundary only.
        """
        prevRow = self.processedPixels[-1]
        iSize = len(prevRow) - 1
        for b in range(iSize):
            for rgb in range(3):
                prevRow[b][rgb] /= rowHeight * self.blkSize
        for rgb in range(3):
            prevRow[iSize][rgb] /= rowHeight * self.finalBlockWidth
        self.processedPixels[-1] = prevRow

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

        result.save(fr"images/result/{processedFileName}.png")
        print(fr"Saved result in images/result/{processedFileName}.png")

    def minecraft(self):
        result = Image.new("RGBA", (textureRes * math.ceil(self.imageSize[0] / self.blkSize), textureRes * math.ceil(self.imageSize[1] / self.blkSize)))
        rawPixels = result.load()
        totalPixels = len(self.processedPixels) * len(self.processedPixels[0])
        progressRaw = 0
        progressPercentage = 1
        progress = 0
        for row in range(len(self.processedPixels)):
            for col in range(len(self.processedPixels[row])):
                nearestBlkDat = getClosestBlockColor(self.processedPixels[row][col])
                blkFile = Image.open(fr"images/raw/blockTextures/{nearestBlkDat[0]}")
                blkFile = blkFile.convert("RGBA")
                blkPixels = blkFile.load()
                for x in range(textureRes):
                    for y in range(textureRes):
                        rawPixels[col * textureRes + x, row * textureRes + y] = blkPixels[x, y]  # pixel color at block position (x, y) here

                if loadingBar:
                    if progress == progressRaw:
                        print(f"\rMinecraftification: {progressPercentage}%", end="")
                        progressPercentage += 1
                        progressRaw += round(totalPixels / 100)
                    progress += 1
        print('')

        if mode == "image":
            result.save(fr"images/result/{processedFileName}_mc.png")
            print(fr"Saved result in images/result/{processedFileName}_mc.png")
        elif mode == "video":
            result.save(fr"images/result/temp/{processedFileName}_mc_{cf}.png")  # delete this entire folder at the end of the program
            print(fr"Saved result in temp/images/result/{processedFileName}_mc_{cf}.png")
        result.close()


def getPixelData(imgObj):
    formattedPixelData = []

    if mode == "image":
        unformattedPixelData = imgObj.load()
        xySize = imgObj.size
        for x in range(xySize[0]):
            formattedPixelData.append([])
            for y in range(xySize[1]):
                formattedPixelData[-1].append(unformattedPixelData[x, y])

    elif mode == "video":
        tempList = imgObj.tolist()
        # swap axes in list
        for y in range(len(tempList[0])):
            formattedPixelData.append([])
        for col in range(len(tempList)):
            for row in range(len(tempList[0])):
                formattedPixelData[row].append(tempList[col][row])

    return formattedPixelData


loadBlocks()

if mode == "image":
    formattedImageData = FormattedImage(getPixelData(Image.open(fr"images/raw/{fileName}.{fileExt}", 'r')))
    myImage = ImageProcessor(formattedImageData)
    myImage.blockProcess()

elif mode == "video":
    myVideo = cv2.VideoCapture(fr"images/raw/{fileName}.{fileExt}")
    videoSize = [int(myVideo.get(cv2.CAP_PROP_FRAME_WIDTH)), int(myVideo.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    videoFramerate = myVideo.get(cv2.CAP_PROP_FPS)
    while True:
        try:
            framerate = float(input(f"Enter a framerate less than or equal to {videoFramerate}: "))
            if framerate > videoFramerate:
                print("Framerate can't be larger than that of the video's!")
            else:
                break
        except ValueError:
            print("Please enter a number!")
            continue

    # convert pixel data in every frame to a format recognized by ImageProcessor
    totalFrames = math.floor(myVideo.get(cv2.CAP_PROP_FRAME_COUNT) * framerate / videoFramerate)
    f = 0
    cf = 0
    while True:
        myVideo.set(cv2.CAP_PROP_POS_FRAMES, math.floor(f))
        exists, frame = myVideo.read()
        if not exists:
            break
        currentFrameImageData = FormattedImage(getPixelData(frame))
        currentFrame = ImageProcessor(currentFrameImageData)
        currentFrame.blockProcess()
        f += videoFramerate / framerate
        if loadingBar:
            print(f"Current frame: {cf}/{totalFrames}")
        cf += 1
    myVideo.release()

    imageNames = []
    imageIdx = []
    for img in os.listdir(fr"images/result/temp"):
        imageNames.append(os.fsdecode(img))

    for i in range(len(imageNames)):
        fName = imageNames[i].split('.')[0]
        imgIdx = ""
        j = len(fName) - 1
        while fName[j] != '_':
            imgIdx += fName[j]
            j -= 1
        imgIdx = imgIdx[::-1]
        imgIdx = int(imgIdx)
        imageIdx.append(imgIdx)

    # bubble sort
    for i in range(len(imageIdx) - 1):
        for j in range(len(imageIdx) - 1 - i):
            if imageIdx[j + 1] < imageIdx[j]:
                tempIdx = imageIdx[j + 1]
                tempImgName = imageNames[j + 1]
                imageIdx[j + 1] = imageIdx[j]
                imageNames[j + 1] = imageNames[j]
                imageIdx[j] = tempIdx
                imageNames[j] = tempImgName

    codec = cv2.VideoWriter_fourcc(*"mp4v")
    processedVideoSize = cv2.imread(fr"images/result/temp/{imageNames[0]}").shape
    videoOutput = cv2.VideoWriter(fr"images/result/{processedFileName}_mc.mp4", codec, framerate, (processedVideoSize[1], processedVideoSize[0]))
    for imageName in imageNames:
        videoOutput.write(cv2.imread(fr"images/result/temp/{imageName}"))  # convert every image to a cv2 image object
    videoOutput.release()

    for tempImg in os.listdir("images/result/temp"):
        os.remove(f"images/result/temp/{tempImg}")
