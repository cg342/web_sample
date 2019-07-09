# this function is to fill all the data of the missing SPn

from collections import OrderedDict
import csv
import time

def fillgap(folderpath):
  inputfile = folderpath + "output_unfilled.csv"

  # D is a dictionary to hold all the rows
  # key: subject code values: list of lists
  # e.g., D['3319GX'] = [[1,106,,,], [2,20.5,,,], [3,80.5,,,]]
  D = OrderedDict()

  # a list for all subject codes
  sublist = []

  with open(inputfile, 'r') as f:
    # skipping the first line which is the header
    header = next(f)
    # read each line of file
    for line in f:
      # get a list out of each row
      linelist = line.rstrip().split(",")
      # first element is subject
      # process by subject code
      if linelist[0] not in sublist:
        sublist.append(linelist[0])
        # initialize the list to be the value of D[key]
        D[linelist[0]]=[]
      D[linelist[0]].append(linelist[1:])
    
  for x in sublist:
  #    start = int(D[x][0][0])     
      cur = 1
      # for looping D[x] all SPn's
      for idx, val in enumerate(D[x]):
        try:
          if cur != int(val[0]):
            toadd=[cur, ".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".","."]
            D[x].insert(idx,toadd)
        except:
          print "exception:"
          print val
          raise
        cur += 1

  timestr = time.strftime("%Y%m%d-%H%M%S")
  with open(folderpath + timestr + "_" + "output.csv", 'wb') as out:
      out.write(header) 
      for x in sublist:
        for row in D[x]:
          
          writer = csv.writer(out)
          out.write(x + ",")
          writer.writerow(row)


