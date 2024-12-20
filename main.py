from PIL import Image


class ImageProcessor:
    def __init__(self, imagePath):
        self.image = Image.open(imagePath)
        self.rectSize = 10

    def getColors(self):
        pass

    def averageColors(self):
        pass


myImage = ImageProcessor(r"images\raw\IMG_2408.jpeg")
