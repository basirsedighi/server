import os


def fixPath(path):

    test = path.split("'\'")
    test.pop()
    newPath = '/'.join(test)
    return newPath

#absolute_path = os.path.dirname(os.path.abspath(__file__))
absolute_path = "jhsdjs/dksjdks/jsdkjsd/sjkdjs"
test = fixPath(absolute_path)

path = absolute_path+"/log/"

print(path)