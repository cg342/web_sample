# all functions for calculating columns for sleep analysis

# getting the data value given a list of data object
# input: a list of "Data"
# return a list of the Data.value
def getDataValue(L):
    newL = []
    for i in L:
        newL.append(i.value)
    return newL

# getting the latS1, latS2, ...
# which are all calculated from time of 8. If there are missing data
# between lights out and the first stage of any of those, then use a '.'. 
# If there are no instances of any of S1, S2, REM, SWS, or PersistSleep, then use '.'
# input: a list of sleep state, and target sleep state 
# output: float / "."
# fixed: return "." if there is 0 in stages
def getLat(L, sleepstate):
    
    lat = next((L.index(i) for i in L if i==sleepstate), None)
    if lat is None:
      return "."
    else:
      if 0 in L[:lat]:
        # return "unscored"
        return "."
      else:
        return lat/2.0

# getting the index of 
# the first epoch of 20 consecutive epoch
# of 1,2,3,4, or 6 
# input: list of sleepstate
# output: [sleep state value, index]
def getPS (L):
    ps=[]
    epo=20
    desired=[1,2,3,4,6]
    count = 0
    # i is index, j is value
    for i,j in enumerate(L):
      if j in desired:
        count += 1 
        # count < 20 and not the last element and next element is not continuous
        if count < epo and i!=len(L)-1 and (L[i+1] not in desired):
          count = 0                         
        elif count >= epo:
          ps.append(L[i-epo+1])
          ps.append(i-epo+1)    
          return ps

# getting # of minutes of each sleep states between 8 and 9
# input: a list of sleep states
# [S1, S2, S3, ..., Other]        
def getCount(L):
    ct1, ct2, ct3, ct4, ctWake, ctRem, ctOther=(0,)*7
    interested = [1,2,3,4,5,6,7,0]
    for i in L:
      # if i in interested:
        if i==1:
          ct1+=1
        elif i==2:
          ct2+=1
        elif i==3:
          ct3+=1
        elif i==4:
          ct4+=1
        elif i==5:
          ctWake+=1
        elif i==6:
          ctRem+=1
        elif i not in [1,2,3,4,5,6,10,8,9]: # anything that is not 1-6 should be counted as Other
          #if i not in [0,7]:
         #   print i
           # print " --> error, other than 0 or 7"
          ctOther+=1
    l = [ct1, ct2, ct3, ct4, ctWake, ctRem, ctOther]
    return [x/2.0 for x in l]

# getting number of minutes of wake(5) after onset of PS
def countWake(L, index):
    if index ==".":
      return "."
    wake = 0
    for item in L[index:]:
      if item == 5:     
          wake += 1 
    return wake/2.0
    
# getting the # of wake episodes >= 1 minute (2 consec epoch) (int)
# intput: list of sleep states, duration of 1,2, or 5 minutues
# output: an integer
def getNWake(L, duration):
    wake = 0
    onset = 0 # onset of wake
    cont = 0  # continuous count of wake
    count = 0 # count of bouts
    # i is index, j is value
    for i,j in enumerate(L):
      if j == 5:
        onset = 1
        cont += 1
        if i!=len(L)-1 and L[i+1]!=5 or i==len(L)-1 and onset == 1:
          onset = 0
          if cont >= duration*2:
            count += 1
          cont = 0

    return count

# -> getting the time of wake(5) uninterrupted by sleep (12346) before 9
# input: a list of sleep states
# output: float (minutes)
def getFinalWake(L):
  sleep = [1,2,3,4,6]
  count = 0
  for i,j in enumerate(reversed(L)):
      if j == 5:
        count += 1
      elif j in sleep:
          return count/2.0
        
# getting the time of 9 minus time of 8-0.5 min
# input: a list of sleep states
# output: float (minutes)
def getLout2Lon(L):
  a = (len(L)-1)/2.0/60 # fixed -> from minutes to hours
  return round(a,2)

# second last column
# sleep stage for the epoch just before each 9
# input: a list of sleep states
# output: int, sleep stage
def SleepStageB49(L):
  sleep = [1,2,3,4,5,6,7,8] # fixed here
  for sleepstage in reversed(L):
      if sleepstage in sleep:
        return sleepstage

# last column
# the sleep stage for the epoch just before Final wake starts 
# (so the last non-5 or 9 epoch)
# input: a list of sleep stages
# output: int, sleep stage
def SleepStageB4FinalWake(L):
  
  sleep = [1,2,3,4,6]
  has9 = False
  has5 = False

  # where the last slp stage is NOT 9
  if L[-1]!=9:
    for sleepstage in reversed(L):
          
      if has5:
        if sleepstage in sleep:
          return sleepstage
      if sleepstage==5:
        has5 = True

  else: # where the last slp is 9  
    for sleepstage in reversed(L):
          
      if has9 and has5:
        if sleepstage in sleep:
          return sleepstage
      if sleepstage==9:
        has9 = True
      elif sleepstage==5:
        has5 = True

# a function to remove elements by index
# input: a list of Data, front or end, index number
# output: a list of Data trimmed
def resetList(L,frontOrEnd,ind):
  if frontOrEnd == 0:
    return L[ind:]
  elif frontOrEnd == 1:
    return L[:ind+1]

# to get path from user
# output: a path (string)          
def getInput():
    
    pathname = raw_input("Enter a path: ")
    if not pathname.endswith("/"):
        pathname += "/"
    return pathname

