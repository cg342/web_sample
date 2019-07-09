import preprocessing as pre 
import read
import check_dup as dup
import allfunctions as func
import fill

# /home/pwm4/Desktop/cg342/sleepprogram_redo/20190419/test2
# /home/pwm4/Desktop/cg342/sleepprogram_redo/20190530
# pathname = func.getInput()
# preprocessing data

def start(pathname):
    # outputMessage[0] is the output path of the file
    outputMessage = [""]
    
    try:
        pre.preprocess(pathname)
        outputMessage.append("Data preprocessing is successful")
    except:
        outputMessage.append("Data preprocessing error!")
    else:
        # run analysis
        outputMessage.append("Analyzing ...")

        try:
            outputpath = read.analyze(pathname)
            outputMessage[0] = outputpath
        except:
            outputMessage.append("Analysis Error!")
        else:
            try:
                # check if there's duplicate line
                dup.check_dup(outputpath)
            except:
                outputMessage.append("Error: Duplicates found!")
            else:
                outputMessage.append("Success: No Duplicates")
                
                try:
                    fill.fillgap(outputpath)
                except: #FunctionTimedOut:
                    # print "Function exceed 3 seconds and was terminated"
                    outputMessage.append("Fill.py error")
                else:   
                    outputMessage.append("Output created successfully!")

    return outputMessage