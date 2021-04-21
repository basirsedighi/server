import os


def fixPath(path):

    test = path.split("\\")
    test.pop()
    newPath = '/'.join(test)
    return newPath

absolute_path = os.path.dirname(os.path.abspath(__file__))

test = fixPath(absolute_path)

path = test+"/log/"

print(path)