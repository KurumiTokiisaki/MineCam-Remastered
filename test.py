import os

imageNames = []
for img in os.listdir(fr"images\result\temp"):
    imageNames.append(os.fsdecode(img))
print(imageNames)
