import csv

with open("_gps.csv") as f:
    lis = [line.split() for line in f]        # create a list of lists
    for i, x in enumerate(lis):              #print the list items 
        print("line{0} = {1}".format(i, x))
