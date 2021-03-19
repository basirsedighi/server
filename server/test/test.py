from bisect import bisect_left

def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before

for n in 

#x = take_closest(lst,k)
#print(x)      
#print([item for item, count in collections.Counter(millispiclist).items() if count > 1])   

#print([item for item, count in collections.Counter(millisk1list).items() if count > 1])