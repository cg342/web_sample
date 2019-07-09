# read.py calls allfunctions.py to read a folder of files
# - reads from a folder of csv file
# - the output appears within a new folder under inputpath
# - the output is a csv file with analysis (mainly) on sleep stages

import csv
from collections import defaultdict
from collections import OrderedDict
import glob
import codecs
import os
import time
import allfunctions as func
import shutil

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

def analyze(inputpath):
    csv_files = glob.glob(inputpath+"*.csv")

    # generate output folder
    timestr = time.strftime("%Y%m%d-%H%M%S")
    outputpath =  inputpath + "output_" + timestr + "/"
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    # dictionary for the final output
    adict = OrderedDict()
    subject_group = []
    output_header = ["Subject","SPn","latS1","latS2","latREM","latSWS","latPersistSLeep","S1",
    "S2","S3","S4","Wake","REM","Other","WAPSO","FinalWake","NWake_1","NWake_2","NWake_5",
    "Lout2Lon","LastSlp","LastSlp_before_finalwake"]

    # initialize the output dictionary keys
    for column_name in output_header:
        adict[column_name] = []

    for filename in csv_files:
        # read from files
        fname = os.path.basename(filename)
        subject = fname[:fname.find('Slp')]
        if subject not in subject_group:
            subject_group.append(subject)
        else:
            # print "duplicate subject:"
            # print filename
            break

        with open(filename, 'r') as f:
            columns = defaultdict(list)
            # read rows into a dictionary format
            reader = csv.DictReader(f,  fieldnames=['subject', 'WPSP', 'labtime', 'sleepstate']) 
            try:
                for row in reader: # read a row as {column1: value1, column2: value2,...}
                    for (k,v) in row.items(): # go over each column name and value 
                        columns[k].append(v)
            except:
                print("Reading error: " + filename)
                raise


        WPSP = columns['WPSP']
        sleepstate = columns['sleepstate']
        slp_list = []
        slp_unit=[]

        # convert list of string to list of integers
        WPSP = list(map(int, WPSP))
        sleepstate = list(map(int, sleepstate))

        ind8 = [i for i, x in enumerate(sleepstate) if x == 8]
        ind9 = [i for i, x in enumerate(sleepstate) if x == 9]
        
        for a,b in zip(ind8,ind9): #consider izip?
            for i in range(a,b+1):
                slp_unit.append(Data(sleepstate[i], i)) # appending sleep stages
            slp_list.append(slp_unit) # slp_list: [Data1,Data2, Data3, ...]
            slp_unit=[]

        slp_list2 = []
        for unit in slp_list:
            # spnlist = [-1, -1, -1, 1, 1,...]
            spnlist = map(int, columns['WPSP'][unit[0].pointer:unit[-1].pointer])

            if any(spns > 0 for spns in spnlist):
                slp_list2.append(unit)

        # index of each first occured sleep state
        # then calculate latency (/2.0)
        for unit in slp_list2:

            unit_start = 0
            flag1 = 0 # if there is a change in unit
            unit_end = -1
            flag2 = 0 # if there is a change in unit
            
            spn = int(columns['WPSP'][unit[0].pointer])
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
        
            # checking spn of 9
            spn9 = int(columns['WPSP'][unit[-1].pointer])
            if spn9 < 0:
                # replace lights out time with scheduled sleep offset
                # find next positive Spn
                # print unit[0].pointer
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
            # print newU
            adict["Subject"].append(columns['subject'][unit[1].pointer])
    #        adict["SPn"].append(abs(int(columns['WPSP'][unit[0].pointer])))
    #        if int(columns['WPSP'][unit[1].pointer]) <0:
    #          print columns['subject'][unit[1].pointer], int(columns['WPSP'][unit[1].pointer])
            adict["SPn"].append(abs(int(columns['WPSP'][unit[0].pointer])))
            adict["latS1"].append(func.getLat(newU, 1))
            adict["latS2"].append(func.getLat(newU, 2))
            adict["latREM"].append(func.getLat(newU, 6))
            
            # latSWS
            if func.getLat(newU, 3)!="." and func.getLat(newU, 4)==".":
                adict["latSWS"].append(func.getLat(newU, 3))

            elif func.getLat(newU, 3)=="." or func.getLat(newU, 4)==".":
                adict["latSWS"].append(".")
            else:
                # checking if 3 appears before 4        
                if func.getLat(newU, 3)<=func.getLat(newU, 4):
                    adict["latSWS"].append(func.getLat(newU, 3))
                else:
                    adict["latSWS"].append(func.getLat(newU, 4)) 

            p = func.getPS(newU) # index of onset of PS
            if not p:
                index="."
                adict["latPersistSLeep"].append(index)
            else:
                index = p[1]
                if 0 in newU[:index]:
                    adict["latPersistSLeep"].append(".")
                else:           
                    adict["latPersistSLeep"].append(index/2.0)

            adict["S1"].append(func.getCount(newU)[0])
            adict["S2"].append(func.getCount(newU)[1])
            adict["S3"].append(func.getCount(newU)[2])
            adict["S4"].append(func.getCount(newU)[3])
            adict["Wake"].append(func.getCount(newU)[4])
            adict["REM"].append(func.getCount(newU)[5])
            adict["Other"].append(func.getCount(newU)[6])
            adict["WAPSO"].append(func.countWake(newU, index))
            fw = func.getFinalWake(newU)
            if fw is None:
                adict["FinalWake"].append(".")
            else:
                adict["FinalWake"].append(fw)
            # get NWake: second parameter is wake time of 1, 2, or 5 minutes
            adict["NWake_1"].append(func.getNWake(newU,1))
            adict["NWake_2"].append(func.getNWake(newU,2))
            adict["NWake_5"].append(func.getNWake(newU,5))
            adict["Lout2Lon"].append(func.getLout2Lon(newU))
            
            # adding 2 more columns:
            lastslp = func.SleepStageB49(newU)
            if lastslp == None:
                adict["LastSlp"].append(".")
            else:
                adict["LastSlp"].append(lastslp)
            
            try:
                lastslpfw = func.SleepStageB4FinalWake(newU)
            except:
                print "slp_stage_b4_finalwake error: "+filename
                print spn
                raise
            
            if lastslpfw == None:
                adict["LastSlp_before_finalwake"].append(".")           
            else:
                adict["LastSlp_before_finalwake"].append(lastslpfw)
        
        # print filename  # print filename after processing each file

    ## write to output
    with open(outputpath + "output_unfilled.csv", "wb") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(adict.keys())
        export_data = zip_longest(*adict.values(), fillvalue = "")
        writer.writerows(export_data)

    return outputpath

