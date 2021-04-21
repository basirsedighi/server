import os


def fixPath(path):

    test = path.split("\\")
    if len(test)>0:

        test.pop()
        newPath = '/'.join(test)
        return newPath
    else:
        return path

absolute_path = os.path.dirname(os.path.abspath(__file__))

test = fixPath(absolute_path)



path = test+"/log/"

print(path)