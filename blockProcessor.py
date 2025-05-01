from PIL import Image
import os

textureRes = Image.open(r"images\raw\blockTextures\dirt.png").size[0]
transparencyTolerance = 200
maxTransparentPixelsAmt = 0


def processMinecraftBlocks():
    blockDir = os.fsencode(r"images/raw/blockTextures")
    processStorage = open(r"images/processed/blockTextures.txt", 'w')
    for blk in os.listdir(blockDir):
        fName = os.fsdecode(blk)
        if fName.endswith(".png"):
            tempResult = averageBlockColor(fr"images/raw/blockTextures\{fName}", fName)
            if tempResult != -1:
                processStorage.writelines(f"{fName}--{tempResult}\n")
    processStorage.close()


def averageBlockColor(path, blockName):
    texture = Image.open(path)
    texture = texture.convert("RGBA")
    pixelDat = texture.load()
    div = textureRes ** 2
    avgColor = [0, 0, 0]
    transparentPixels = 0
    for x in range(textureRes):
        for y in range(textureRes):
            if pixelDat[x, y][3] <= transparencyTolerance:
                transparentPixels += 1
            for c in range(3):
                avgColor[c] += pixelDat[x, y][c]

    if (transparentPixels <= maxTransparentPixelsAmt) and ((blockName != "debug.png") and (blockName != "debug2.png")):
        for c in range(3):
            avgColor[c] /= div
            avgColor[c] = round(avgColor[c])
    else:
        avgColor = -1

    return avgColor


processMinecraftBlocks()
