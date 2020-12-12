import pandas as pd
import datetime

deviceIn = r'C:\Users\esgel\OneDrive\Documents\workfile alc close.txt'
droneIn = r'C:\Users\esgel\OneDrive\Documents\Aug-9th-2020-04-33PM-last Flight-Airdata.xlsx'
compiledOut = r'C:\Users\esgel\OneDrive\Documents\alcClosCompiled.xlsx'

#designates irregular entries in drone data so they can be removed
def mark11thMilliseconds(df):
    entriesToDelete = []
    newList = []
    currSec = df['datetime(utc)'][0].second
    repeatFlag = 0
    for i in range(0,len(df)):
        if (df['datetime(utc)'][i].second != currSec):
            repeatFlag = 0
            currSec = df['datetime(utc)'][i].second
        if (df['datetime(utc)'][i].microsecond == 0):
            if (repeatFlag == 1):
                entriesToDelete.append(i)
            repeatFlag = 1
    return (entriesToDelete)
        
#assigns 10th of second timestamp to drone data entries
def setMicoseconds(df, offset):
    for i in range(0,10-offset):
        df['datetime(utc)'][i]= df['datetime(utc)'][i].replace(microsecond = (offset+i)*100000)
    firstIter = 10-offset
    currentIter = 10-offset
    prevSecond = df['datetime(utc)'][0].second
    while (currentIter < len(df)-10):
        currentSec = df['datetime(utc)'][currentIter].second
        
        for n in range(0,10):
            if (currentSec != df['datetime(utc)'][currentIter].second):
                break
            df['datetime(utc)'][currentIter]= df['datetime(utc)'][currentIter].replace(microsecond = (n)*100000)
            currentIter+=1
        prevSecond +=1

            
    entriesToRemove = mark11thMilliseconds(df)

    newMap = {}
    for key in df:
        newMap[key] = []
        for i in range(0,len(df)):
            if i not in entriesToRemove:
                newMap[key].append(df[key][i])
    newDataFrame = pd.DataFrame(data=newMap) 
    return (newDataFrame)
    

#gets starting time in 10th of second
def getStartOffset(df):
    ticks = 0
    startTimeSeconds = df['datetime(utc)'][0]
    #print (startTimeSeconds.microsecond)
    for i in range(0,10):
        
        if (df['datetime(utc)'][i] == startTimeSeconds):
            ticks += 1
    offset = 10 - ticks
    return (offset)

#merges drone and device data into single dataset
def mergeData(droneData,deviceData):
    newMap = {}
    for key in droneData:
        newMap[key] = []
    newMap['deviceData'] = []
    newMap['deviceTime'] = []
    newMap['estimateTime'] = []
    currDroneTime = []
    currDeviceTime = []
    prevDeviceTime = [99999,99999,99999]
    for i in range(0,len(deviceData)):
        deviceTimeParse = deviceData[i][1].strip(" ").split(" ")
        deviceTimeParse = deviceTimeParse[1]
        deviceTimeParse = deviceTimeParse.split(":")
        currDeviceTime.append(int(deviceTimeParse[1]))
        deviceTimeParse = str(deviceTimeParse[2]).split(".")
        currDeviceTime.append(int(deviceTimeParse[0]))
        deviceTimeParse = round(int(deviceTimeParse[1])/100000)
        currDeviceTime.append(int(deviceTimeParse))
        if (currDeviceTime != prevDeviceTime) :
            for n in range(0,len(droneData)):
                droneHour = (droneData['datetime(utc)'][n].hour)
                droneMin = (droneData['datetime(utc)'][n].minute)
                droneSec = (droneData['datetime(utc)'][n].second)
                drone10thSec = (int(droneData['datetime(utc)'][n].microsecond/100000))
                currDroneTime.append(droneMin)
                currDroneTime.append(droneSec)
                currDroneTime.append(drone10thSec)
                if (currDeviceTime == currDroneTime):
                    for key in droneData:
                        newMap[key].append(droneData[key][n])   
                    newMap['deviceData'].append(deviceData[i][0])
                    newMap['deviceTime'].append(deviceData[i][1])
                    newMap['estimateTime'].append(str(droneHour)+":"+str(droneMin)+":"+str(droneSec)+"."+str(drone10thSec))
                    break
                currDroneTime = []   
        prevDeviceTime = currDeviceTime
        currDeviceTime = []
    newDataFrame = pd.DataFrame(data=newMap) 
    newDataFrame.to_excel(compiledOut, index = False)
    print(newDataFrame)
    
#gets data from device and parses it
def getDeviceData(deviceDataFile):
    deviceDataList = []
    currDeviceData = []
    for (columnName, columnData) in deviceDataFile.iteritems(): 
    
        #print('Colunm Name : ', columnName) 
        #print('Column Contents : ', columnData.values) 
        
        if ("r" in columnName):
            
            splitVal = columnName.split("'")
            currDeviceData.append(splitVal[0].strip("\\r\\n"))
            #print(splitVal)
            deviceDataList.append([currDeviceData,splitVal[1].strip("b")])
            if (len(splitVal)>2):
                currDeviceData = ["b'"+splitVal[2]]
            #print ("r\n")
        else:
            currDeviceData.append(columnName)    
    return deviceDataList

df = pd.read_excel (droneIn)
read_file = pd.read_csv(deviceIn)
deviceDataList = getDeviceData(read_file)        
offset = getStartOffset(df)
droneData = setMicoseconds(df,offset)
mergeData(droneData, deviceDataList)
