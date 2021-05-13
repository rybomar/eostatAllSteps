import struct
import numpy as np
import RasterObject
import pandas as pd


class StatsReader(object):
    statsBinFilePath = ''
    segmentsFilePath = ''
    ids1basedTifFilePath = ''
    objects = []

    def __init__(self):
        self.statsBinFilePath = ''
        self.objects = []

    def readFromBinFileAsPdDataFrame(self, binFilePath):
        print('Loading ' + str(binFilePath))
        self.statsBinFilePath = binFilePath
        PdHeader = []
        objectsNum = 0
        positionOnList = 0
        dataWidth = 0
        with open(binFilePath, "rb") as f:
            bin4float = f.read(4)
            try:
                while bin4float:
                    decodedValue = struct.unpack('f', bin4float)
                    decodedValue = decodedValue[0]
                    if decodedValue == -1000:
                        objectsNum = objectsNum + 1
                    if objectsNum == 1:
                        if positionOnList == 3:
                            PdHeader.append('id')
                            dataWidth = int(decodedValue)
                        if positionOnList > 3:
                            PdHeader.append(str(positionOnList - 3))
                        positionOnList = positionOnList + 1
                    bin4float = f.read(4)
            except:
                a=2

        PdHeader.append('class')
        allObjectsMatrix = np.zeros((objectsNum, dataWidth+2))
        print('Found ' + str(objectsNum) + ' objects.')
        with open(binFilePath, "rb") as f:
            bin4float = f.read(4)
            positionOnList = 0
            classNumber = 1001
            index = -1
            while bin4float:
                decodedValue = struct.unpack('f', bin4float)
                decodedValue = decodedValue[0]
                # BEGIN
                if decodedValue == -1000:
                    positionOnList = 0
                    index = index + 1
                # ID
                if positionOnList == 1:
                    readId = decodedValue
                    allObjectsMatrix[index, positionOnList-1] = readId
                # class
                if positionOnList == 2:
                    classNumber = decodedValue
                    allObjectsMatrix[index, dataWidth + 1] = classNumber
                # values
                if positionOnList > 3:
                    allObjectsMatrix[index, positionOnList - 3] = decodedValue
                positionOnList = positionOnList + 1
                bin4float = f.read(4)
        df = pd.DataFrame(allObjectsMatrix, columns=PdHeader)
        print('Loaded')
        return df

    def readFromBinFile(self, binFilePath):
        self.statsBinFilePath = binFilePath
        with open(binFilePath, "rb") as f:
            floatList = np.zeros(0)
            bin4float = f.read(4)
            positionOnList = 0
            countData = 0
            classNumber = 1001
            self.objects = []
            while bin4float:
                decodedValue = struct.unpack('f', bin4float)
                decodedValue = decodedValue[0]
                # BEGIN
                if decodedValue == -1000:
                    positionOnList = 0
                    floatList = np.zeros(0)
                    readId = -1
                    classNumber = 1001
                # ID
                if positionOnList == 1:
                    readId = decodedValue
                # Values
                if positionOnList == 2:
                    classNumber = decodedValue
                if positionOnList == 3:
                    countData = decodedValue
                    floatList = np.zeros(countData)
                if positionOnList > 3:
                    #todo: test it!
                    #floatList.append(decodedValue)
                    index = positionOnList - 4
                    floatList[index] = decodedValue
                if positionOnList > 3 and len(floatList) == countData:
                    ro = RasterObject.RasterObject([])
                    ro.assignId(readId)
                    ro.fillFeatures(floatList)
                    ro.assignClass(classNumber)
                    self.objects.append(ro)
                # if len(objects) > 30000:#debug/test
                #    break;
                positionOnList = positionOnList + 1
                bin4float = f.read(4)

    def selectObjectsByPoints(self, segmentsTifFIlePath, ids1basedTifFilePath, vectorFilePath, columnName):
        self.segmentsFilePath = segmentsTifFIlePath