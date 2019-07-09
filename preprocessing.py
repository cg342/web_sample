# to find the problem with files 
# check if they have the right lights out/on sequences

import csv
from collections import defaultdict
from collections import OrderedDict
import glob
import codecs
import os
import time
import allfunctions as func
import shutil
import logging

logging.basicConfig(filename="_pre.log_", level=logging.ERROR)

try:
    # Python 3
    from itertools import zip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest as zip_longest

# A Data object holds 2 properties:
# 1. value (str)
# 2. original position 

class Data(object):
    value=0
    pointer=-1

    def __init__(self, value, pointer):
        self.value = value
        self.pointer = pointer   
    
    def resetData(self, value, pointer):
        self.value = value
        self.pointer = pointer 

def check8_9(WPSP, ind8, ind9):
    rg = min(len(ind8), len(ind9))
    for i in range(rg):
        # print WPSP[ind9[i]]
        if WPSP[ind9[i]] < 0: # if index of 9 is neg
            new9 = abs(WPSP[ind9[i]]) - 1
        else:
            new9 = abs(WPSP[ind9[i]])
        if abs(WPSP[ind8[i]]) != new9:
            return abs(WPSP[ind8[i]])
    return "N/A"

def preprocess(inputpath):

    errmsg = []
    csv_files = glob.glob(inputpath+"*.csv")
    # dictionary for the final output
    adict = OrderedDict()

    output_header = ["Subject","SPn","latS1","latS2","latREM","latSWS","latPersistSLeep","S1",
    "S2","S3","S4","Wake","REM","Other","WAPSO","FinalWake","NWake_1","NWake_2","NWake_5","Lout2Lon"]

    # initialize the output dictionary keys
    for column_name in output_header:
        adict[column_name] = []

    for filename in csv_files:
        # read from files
        with open(filename, 'r') as f:
            columns = defaultdict(list)
            # read rows into a dictionary format
            reader = csv.DictReader(f,  fieldnames=['subject', 'WPSP', 'labtime', 'sleepstate']) 
            for row in reader: # read a row as {column1: value1, column2: value2,...}
                    for (k,v) in row.items(): # go over each column name and value 
                        columns[k].append(v)

        WPSP = columns['WPSP']
        sleepstate = columns['sleepstate']
        slp_list = []
        slp_unit=[]

        # convert list of string to list of integers
        WPSP = list(map(int, WPSP))
        # print sleepstate[:100]
        # sleepstate = list(map(int, sleepstate))


        for item in sleepstate:
            try:
                int(item)
            except:
                logging.error(str(item))
                raise

        sleepstate = map(int, sleepstate)

        ind8 = [i for i, x in enumerate(sleepstate) if x == 8]
        ind9 = [i for i, x in enumerate(sleepstate) if x == 9]

        if len(ind8) != len(ind9): # file has unequal number of 8 and 9
            logging.error("Unequal number of 8 and 9 error: " + filename)
            logging.error("Issue occured in spn: " + str(check8_9(WPSP, ind8, ind9)))
            #logging.error("\n".join(x for x in errmsg))
            raise 
        else:        
            for a,b in zip(ind8,ind9):
                if a>b:
                    logging.error("Unmatching 8 and 9 error: " + filename)
                    logging.error("Issue occured in spn: " + str(check8_9(WPSP, ind8, ind9)))
                    #logging.error("\n".join(x for x in errmsg))
                    raise

        for a,b in zip(ind8,ind9):
            for i in range(a,b+1):
                # slp_unit: [Data1, Data2, Data3, ...]
                slp_unit.append(Data(sleepstate[i], i)) # appending sleep stages
            slp_list.append(slp_unit) # slp_list:[[d1, d2, ...],[d10, d11, ...], ...]
            slp_unit=[]
        
        for unit in slp_list:

            unit_start = 0
            flag1 = 0 # if there is a change in unit
            unit_end = -1
            flag2 = 0 # if there is a change in unit
            
            #Spn of 8
            spn = int(columns['WPSP'][unit[0].pointer])
            # checking spn of 9
            spn9 = int(columns['WPSP'][unit[-1].pointer])

            if len(unit)<10:

                logging.error("very short sleep stage list, spn of 8 is:" + str(spn))
                raise
            try:
                if spn < 0:
                    # replace lights out time with scheduled sleep offset
                    # find next positive Spn
                    indof8 = unit[unit_start].pointer
                    # print indof8
                    # print columns['WPSP'][unit[0].pointer]
                    while True:
                        flag1 = 1
                        indof8 += 1
                        unit_start += 1
                        if int(columns['WPSP'][indof8]) > 0:
                            # unit[0].resetData(int(columns['sleepstate'][indof8]),indof8)
                            break
            
                if spn9 < 0:
                    # replace lights out time with scheduled sleep offset
                    # find next positive Spn
                    indof9 = unit[unit_end].pointer
                    # print indof8
                    # print columns['WPSP'][unit[0].pointer]
                    while True:
                        flag2 = 1
                        indof9 -= 1
                        unit_end -= 1

                        if int(columns['WPSP'][indof9]) > 0:

                            # unit[-1].resetData(int(columns['sleepstate'][indof9]),indof9)
                            break
                
                # making the Data.value into a new list
                # newU is [8,,,,9] or [5,,,,,9]
                if flag1 == 1 and flag2 == 1:
                    newU = func.getDataValue(unit[unit_start:unit_end+1])
                elif flag2 == 0:
                    newU = func.getDataValue(unit[unit_start:])
                elif flag1 == 0:
                    newU = func.getDataValue(unit[:unit_end+1])
                else:
                    newU = func.getDataValue(unit)
            except:
                logging.error("out of bound between lights out and lights on" + str(spn))

                raise
        # print filename