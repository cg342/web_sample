# check if there is duplicate spn in the unfilled output

from collections import OrderedDict
import csv


#folderpath = "/home/pwm4/Desktop/cg342/sleepprogram_redo/20190419_ready/output_20190419-153912/"

# this function is to fill all the data of the missing SPn
def check_dup(folderpath):
  inputfile = folderpath + "output_unfilled.csv"

  # a dictionary to hold all the rows
  # key: subject code values: list of lists / list of rows
  # e.g., D['3319GX'] = [[1,106,,,], [2,20.5,,,], [3,80.5,,,]]
  D = OrderedDict()

  # a list for all subject codes
  sublist = []

  with open(inputfile, 'r') as f:
    next(f)
    # read each line of file
    for line in f:
      # get a list out of each row
      linelist = line.rstrip().split(",")
      # first element is subject
      # process by subject code
      if linelist[0] not in sublist:
        sublist.append(linelist[0])
        # initialize the list to be the value of D[subjectcode]
        D[linelist[0]]=[]
      D[linelist[0]].append(linelist[1:])
    
  for x in sublist:
  #    start = int(D[x][0][0])     
      cur = 0
      spnlist = []
      # for looping D[x] all SPn's
      for idx, val in enumerate(D[x]):
        # val[0] is the SPn of the row
        spnlist.append(int(val[0]))
      
      for idx, spn in enumerate(spnlist):
        if idx==0:
          prev = spn
        else:
          if prev==spn:
            print "dup!"
            print x, spn
          prev = spn
          