import random

import numpy as np
import pandas as pd
import traceback


class FeaturesMangerS1S2:
    """description of class"""

    def __init__(self):
        self.averagesS1 = np.empty([0, 0])
        self.OneDateRatiosS1 = []
        self.MultiDateRatiosS1 = []
        self.formulasS1 = []
        self.averagesS2 = np.empty([0, 0])
        self.likeNDVIS2 = []
        self.MultiDateRatiosS2 = []
        self.allFeatures = []
        self.ids = []
        self.classNumbers = []
        self.namesAveragesS1 = []
        self.namesOneDateRatiosS1 = []
        self.namesLikeNDVIS1 = []
        self.namesMultiDateRatiosS1 = []
        self.namesAveragesS2 = []
        self.namesLikeNDVIS2 = []
        self.namesMultiDateRatiosS2 = []
        self.namesBandsS1 = []
        self.namesBandsS2 = []
        self.bandCountS1 = 0
        self.bandCountS2 = 0
        self.currentDeleted = 0

        self.numbersOfTerms = 0
        self.namesBandsS1.append('TA')
        self.namesBandsS1.append('TH')
        self.namesBandsS1.append('TL1')
        self.namesBandsS1.append('T11')
        self.namesBandsS1.append('T12')
        self.namesBandsS1.append('T22')

        self.bandCountS2 = 9
        if self.bandCountS2 == 4:
            self.namesBandsS2.append('B2')
            self.namesBandsS2.append('B3')
            self.namesBandsS2.append('B4')
            self.namesBandsS2.append('B8')
        if self.bandCountS2 == 6:
            self.namesBandsS2.append('B2')
            self.namesBandsS2.append('B3')
            self.namesBandsS2.append('B4')
            self.namesBandsS2.append('B8A')
            self.namesBandsS2.append('B11')
            self.namesBandsS2.append('B12')
        if self.bandCountS2 > 6:
            self.namesBandsS2.append('B2')
            self.namesBandsS2.append('B3')
            self.namesBandsS2.append('B4')
            self.namesBandsS2.append('B5')
            self.namesBandsS2.append('B6')
            self.namesBandsS2.append('B7')
            self.namesBandsS2.append('B8A')
            self.namesBandsS2.append('B11')
            self.namesBandsS2.append('B12')

        self.bandCountS1 = len(self.namesBandsS1)
        self.bandCountS2 = len(self.namesBandsS2)

    def readRefS2DataFromCSV(self, csvPath):
        testSet = pd.read_csv(csvPath)
        features = testSet.columns[1:testSet.shape[1] - 2]
        featuresValues = testSet[features].values
        self.averagesS2 = featuresValues
        classNumsM1 = testSet['class']
        self.classNumbers = classNumsM1 * -1 - 1
        self.classNumbers = self.classNumbers.to_numpy()
        self.ids = testSet['id']
        self.ids = self.ids.to_numpy()
        for t in range(0, self.averagesS2.shape[1], self.bandCountS2):
            for bName in self.namesBandsS2:
                self.namesAveragesS2.append('#T' + str(t + 1) + bName)

    def readS1DataFromDataFrame(self, dataFrame):
        self.prepareReadS1Data(dataFrame)

    def readS2DataFromDataFrame(self, dataFrame):
        self.prepareReadS2Data(dataFrame)

    def readRefS1DataFromXlsx(self, xlsxPath):
       testSet = pd.read_excel(xlsxPath)
       self.prepareReadS1Data(testSet)

    def readRefS1DataFromCSV(self, csvPath):
        testSet = pd.read_csv(csvPath)
        # testSet = csv.reader(csvPath)
        self.prepareReadS1Data(testSet)

    def readRefS1DataFromCSVs(self, csvPaths):
        testSet= []
        counter = 0
        for csvPath in csvPaths:
            if counter == 0:
                testSet = pd.read_csv(csvPath)
                if 'Unnamed' in testSet.columns[-1]:
                    testSet = testSet.drop(columns=['Unnamed'])
            else:
                testSetOne = pd.read_csv(csvPath)
                if 'Unnamed' in testSetOne.columns[-1]:
                    testSetOne = testSet.drop(columns=['Unnamed'])
                featuresColumns = testSetOne.columns[1:testSetOne.shape[1] - 1]  # todo: zmiana numerow w kolumnach, bo zawsze jest t#1, a wczytujac kolejny należy zmieniać na t#2, t#3 itd.
                data_in_csv = testSet[featuresColumns]
                test_set_column_count = len(testSet.columns)
                testSet.insert(test_set_column_count-2, featuresColumns, data_in_csv, allow_duplicates=True)
                # todo: remove 1 and last column, add to testSet - check is it work?
            counter += 1
        self.prepareReadS1Data(testSet)

    def readS1DataFromObjectList(self, objectList):
        N = len(objectList)

    def prepareReadS1Data(self, data):
        if len(data) > 0:
            testSet = data
            if 'Unnamed' in testSet.columns[-1]:
                featuresColumns = testSet.columns[1:testSet.shape[1] - 2]
            else:
                featuresColumns = testSet.columns[1:testSet.shape[1] - 1]
            self.namesAveragesS1 = featuresColumns
            featuresValues = testSet[featuresColumns].values
            idsS1 = testSet['id']
            idsS1 = idsS1.to_numpy()
            classNumsM1 = testSet['class']
            # if len(self.ids) == 0:
            self.ids = idsS1
            self.classNumbers = classNumsM1 * -1 - 1
            self.classNumbers = self.classNumbers.to_numpy()
            self.averagesS1 = np.zeros((self.ids.shape[0], featuresValues.shape[1]))
            self.averagesS1 = featuresValues

    def prepareReadS2Data(self, data):
        if len(data) > 0:
            testSet = data
            if 'Unnamed' in testSet.columns[-1]:
                featuresColumns = testSet.columns[1:testSet.shape[1] - 2]
            else:
                featuresColumns = testSet.columns[1:testSet.shape[1] - 1]
            self.namesAveragesS1 = featuresColumns
            featuresValues = testSet[featuresColumns].values
            idsS2 = testSet['id']
            idsS2 = idsS2.to_numpy()
            classNumsM1 = testSet['class']
            # if len(self.ids) == 0:
            self.ids = idsS2
            self.classNumbers = classNumsM1 * -1 - 1
            self.classNumbers = self.classNumbers.to_numpy()
            self.averagesS2 = np.zeros((self.ids.shape[0], featuresValues.shape[1]))
            self.averagesS2 = featuresValues

    def prepareS1Features(self):
        if len(self.averagesS1) > 0:
            self.FillFormulas()
            self.FillRatiosS1()

    def FillRatiosS1ForAll(self):
        ri = 0
        bandCount = 6
        numOfAverages = int(bandCount * self.numbersOfTerms)
        numbersOfTerms = int(self.numbersOfTerms)
        eps = 0.00001
        for i in range(0, numOfAverages, bandCount):
            T11ind = i + 3
            T12ind = i + 4
            T22ind = i + 5
            T11 = self.averagesS1[:, T11ind]
            T12 = self.averagesS1[:, T12ind]
            T22 = self.averagesS1[:, T22ind]

            d = T11 + T12 + eps
            ratio = (T11 - T12) / d
            self.OneDateRatiosS1[:, ri] = ratio
            ri = ri + 1

            d = T11 + T22 + eps
            ratio = (T11 - T22) / d
            self.OneDateRatiosS1[:, ri] = ratio
            ri = ri + 1

            d = T12 + T22 + eps
            ratio = (T12 - T22) / d
            self.OneDateRatiosS1[:, ri] = ratio
            ri = ri + 1
        # multidate
        ri = 0
        for k in range(6):
            for d1 in range(numbersOfTerms):
                for d2 in range(d1 + 1, numbersOfTerms):
                    indD1 = d1 * 6 + k
                    indD2 = d2 * 6 + k
                    Tkd1 = self.averagesS1[:, indD1]
                    Tkd2 = self.averagesS1[:, indD2]
                    d = Tkd1 + Tkd2 + eps
                    multiTempRatio = (Tkd1 - Tkd2) / d
                    self.MultiDateRatiosS1[:, ri] = multiTempRatio
                    ri = ri + 1

    def FillRatiosS1ForObject(self, objIndex):
        o = objIndex
        ri = 0
        bandCount = 6
        numOfAverages = int(bandCount * self.numbersOfTerms)
        numbersOfTerms = int(self.numbersOfTerms)
        for i in range(0, numOfAverages, bandCount):
            T11ind = i + 3
            T12ind = i + 4
            T22ind = i + 5

            T11 = self.averagesS1[o, T11ind]
            T12 = self.averagesS1[o, T12ind]
            T22 = self.averagesS1[o, T22ind]

            ratio1 = 0
            ratio2 = 0
            ratio3 = 0

            d1 = T11 + T12
            if d1 != 0:
                ratio1 = (T11 - T12) / d1
            self.OneDateRatiosS1[o, ri] = ratio1
            ri = ri + 1

            d2 = T11 + T22
            if d2 != 0:
                ratio2 = (T11 - T22) / d2
            self.OneDateRatiosS1[o, ri] = ratio2
            ri = ri + 1

            d3 = T12 + T22
            if d3 != 0:
                ratio3 = (T12 - T22) / d3
            self.OneDateRatiosS1[o, ri] = ratio3
            ri = ri + 1

        # multidate
        ri = 0
        for k in range(6):
            for d1 in range(numbersOfTerms):
                for d2 in range(d1 + 1, numbersOfTerms):
                    indD1 = d1 * 6 + k
                    indD2 = d2 * 6 + k
                    Tkd1 = self.averagesS1[o, indD1]
                    Tkd2 = self.averagesS1[o, indD2]
                    d = Tkd1 + Tkd2
                    multiTempRatio = 0
                    if d != 0:
                        multiTempRatio = (Tkd1 - Tkd2) / d
                    self.MultiDateRatiosS1[o, ri] = multiTempRatio
                    ri = ri + 1

    def FillRatiosS1(self):
        if len(self.averagesS1) > 0:
            numObjects = self.averagesS1.shape[0]
            self.numbersOfTerms = int(self.averagesS1.shape[1] / self.bandCountS1)
            numbersOfTerms = int(self.numbersOfTerms)
            self.OneDateRatiosS1 = np.empty((numObjects, numbersOfTerms * 3))
            self.MultiDateRatiosS1 = np.empty((numObjects, 6 * int((numbersOfTerms * numbersOfTerms - 2) / 2)))
            self.FillRatiosS1ForAll()

    def addS2likeNDVI(self):
        if len(self.averagesS2) == 0:
            return
        bandCount = 9
        T = int(self.averagesS2.shape[1] / bandCount)
        numObjects = self.averagesS2.shape[0]
        aboveDiag = int((bandCount * (bandCount - 1)) / 2)
        self.likeNDVIS2 = np.zeros((numObjects, aboveDiag * T), dtype=np.float32)
        for o in range(numObjects):
            for i in range(T):
                ri = 0
                for b1 in range(bandCount):
                    for b2 in range(b1 + 1, bandCount):
                        if o == 0:
                            #featureName = '#T' + str(i + 1) + self.namesBandsS2[b1] + 'ratio' + '#T' + str(i + 1) + self.namesBandsS2[b2]
                            featureName = str(ri)
                            self.namesLikeNDVIS2.append(featureName)
                        v0 = self.averagesS2[o, i * bandCount + b1]
                        v1 = self.averagesS2[o, i * bandCount + b2]
                        ratio = 0
                        d = v0 + v1
                        if d != 0:
                            ratio = (v0 - v1) / d
                        self.likeNDVIS2[o, i * bandCount + ri] = ratio
                        ri = ri + 1

    def addS1likeNDVI(self):
        if len(self.averagesS1) == 0:
            return
        bandCount = 6
        T = int(self.averagesS1.shape[1] / bandCount)
        numObjects = self.averagesS1.shape[0]
        aboveDiag = int((bandCount * (bandCount - 1)) / 2)
        self.likeNDVIS1 = np.zeros((numObjects, aboveDiag * T), dtype=np.float32)
        for o in range(numObjects):
            for i in range(T):
                ri = 0
                for b1 in range(bandCount):
                    for b2 in range(b1 + 1, bandCount):
                        if o == 0:
                            #featureName = '#T' + str(i + 1) + self.namesBandsS2[b1] + 'ratio' + '#T' + str(i + 1) + self.namesBandsS2[b2]
                            featureName = str(ri)
                            self.namesLikeNDVIS1.append(featureName)
                        v0 = self.averagesS2[o, i * bandCount + b1]
                        v1 = self.averagesS2[o, i * bandCount + b2]
                        ratio = 0
                        d = v0 + v1
                        if d != 0:
                            ratio = (v0 - v1) / d
                        self.likeNDVIS2[o, i * bandCount + ri] = ratio
                        ri = ri + 1

    def FillFormulas(self):
        numObjects = self.averagesS1.shape[0]
        T = int(self.averagesS1.shape[1] / self.bandCountS1)
        aboveDiag = int((T * (T - 1)) / 2)
        allFormulasCount = aboveDiag * 2 * self.bandCountS1
        self.formulasS1 = np.zeros((numObjects, allFormulasCount), dtype=np.float32)
        ri = 0
        for featureType in range(0, self.bandCountS1, 1):
            for T1 in range(T):
                for T2 in range(T1+1, T):
                    if ri == 1632:
                        a=3
                    indexT1 = T1 * self.bandCountS1 + featureType
                    indexT2 = T2 * self.bandCountS1 + featureType
                    a = T1 + 1
                    b = T2 + 1
                    A = self.averagesS1[:, indexT1]
                    B = self.averagesS1[:, indexT2]
                    formula1 = 0
                    formula2 = 0
                    formula1 = A - ((B*a - A * b) / (a - b)) / a
                    formula2 = (B * a - A * b) / (a - b)
                    self.formulasS1[:, ri] = formula1
                    ri = ri+1
                    self.formulasS1[:, ri] = formula2
                    ri = ri + 1

    def addMultiTempS2Ratio(self):
        if len(self.averagesS2) == 0:
            return
        bandCount = 9
        T = int(self.averagesS2.shape[1] / bandCount)
        numObjects = self.averagesS2.shape[0]
        aboveDiag = int((T * (T - 1)) / 2)
        mDateRatioSize = (numObjects, bandCount * aboveDiag)
        self.MultiDateRatiosS2 = np.zeros(mDateRatioSize)
        for o in range(numObjects):
            ri = 0
            for b in range(0, bandCount):
                for t1 in range(T):
                    t1v = self.averagesS2[o, t1 * bandCount + b]
                    for t2 in range(t1 + 1, T):
                        try:
                            if o == 0:
                                # featurename = '#T' + str(t1 + 1) + self.namesBandsS2[b] + 'ratio' + '#T' + str(t2 + 1) + \
                                #               self.namesBandsS2[b]
                                featurename = 'A' + str(ri)
                                self.namesMultiDateRatiosS2.append(featurename)
                            t2v = self.averagesS2[o, t2 * bandCount + b]
                            mratio = 0
                            d = t1v + t2v
                            if d != 0:
                                mratio = (t1v - t2v) / d
                            self.MultiDateRatiosS2[o, ri] = mratio
                            ri = ri + 1
                        except Exception as e:
                            print(str(e))
                            print(traceback.format_exc())

    def printClassStats(self):
        print('Class id: number of points')
        for c in np.unique(self.classNumbers):
            print(str(c), ": ", str(np.sum(self.classNumbers == c)))

    def prepareS2Features(self):
        if len(self.averagesS2) > 0:
            self.addS2likeNDVI()
            self.addMultiTempS2Ratio()

    def deleteWrongData(self):
        self.deleteLackData()

    def getS1Features(self):
        self.deleteWrongData()
        S1All = self.averagesS1
        if len(self.OneDateRatiosS1) > 0 and self.OneDateRatiosS1.shape[0] > 0:
            S1All = np.concatenate((S1All, self.OneDateRatiosS1), axis=1)
        if len(self.MultiDateRatiosS1) > 0 and self.MultiDateRatiosS1.shape[0] > 0:
            S1All = np.concatenate((S1All, self.MultiDateRatiosS1), axis=1)
        if len(self.formulasS1) > 0:
            S1All = np.concatenate((S1All, self.formulasS1), axis=1)
        trainingData = {'ids': self.ids, 'classNums': self.classNumbers, 'featuresValues': S1All}
        self.printClassStats()
        return trainingData

    def getS2Features(self):
        self.deleteWrongData()
        self.prepareS2Features()
        S2AllFeatures = np.concatenate((self.averagesS2, self.likeNDVIS2, self.MultiDateRatiosS2), axis=1)
        trainingData = {'ids': self.ids, 'classNums': self.classNumbers, 'featuresValues': S2AllFeatures}
        self.printClassStats()
        return trainingData

    def getS2BasicFeatures(self):
        self.deleteWrongData()
        self.prepareS2Features()
        S2AllFeatures = self.averagesS2
        trainingData = {'ids': self.ids, 'classNums': self.classNumbers, 'featuresValues': S2AllFeatures}
        return trainingData

    def getS2BasicLikeNDVIFeatures(self):
        self.deleteWrongData()
        self.prepareS2Features()
        S2AllFeatures = np.concatenate((self.averagesS2, self.likeNDVIS2), axis=1)
        trainingData = {'ids': self.ids, 'classNums': self.classNumbers, 'featuresValues': S2AllFeatures}
        return trainingData

    def getS2BasicMultiDateFeatures(self):
        self.deleteWrongData()
        self.prepareS2Features()
        S2AllFeatures = np.concatenate((self.averagesS2, self.MultiDateRatiosS2), axis=1)
        trainingData = {'ids': self.ids, 'classNums': self.classNumbers, 'featuresValues': S2AllFeatures}
        return trainingData

    def getAllFeatures(self, deleteWrongData=True):
        # self.printClassStats(self.classNumbers)
        if deleteWrongData:
            self.deleteWrongData()
        if self.averagesS1.shape[0] > 0:
            self.prepareS1Features()
        if self.averagesS2.shape[0] > 0:
            self.prepareS2Features()

        S1All = self.averagesS1
        if len(self.OneDateRatiosS1) > 0 and self.OneDateRatiosS1.shape[0] > 0:
            S1All = np.concatenate((S1All, self.OneDateRatiosS1), axis=1)
        if len(self.MultiDateRatiosS1) > 0 and self.MultiDateRatiosS1.shape[0] > 0:
            S1All = np.concatenate((S1All, self.MultiDateRatiosS1), axis=1)
        if len(self.formulasS1) > 0:
            S1All = np.concatenate((S1All, self.formulasS1), axis=1)
        S2All = self.averagesS2
        if len(self.likeNDVIS2) > 0 and self.likeNDVIS2.shape[0] > 0:
            S2All = np.concatenate((S2All, self.likeNDVIS2), axis=1)
        if len(self.MultiDateRatiosS2) > 0 and self.MultiDateRatiosS2.shape[0] > 0:
            S2All = np.concatenate((S2All, self.MultiDateRatiosS2), axis=1)
        self.allFeatures = np.zeros((0, 0))
        if len(S1All) > 0 and S1All.shape[0] > 0:
            if self.allFeatures.shape[0] == S1All.shape[0]:
                self.allFeatures = np.concatenate((self.allFeatures, S1All), axis=1)
            else:
                self.allFeatures = S1All
        if len(S2All) > 0 and S2All.shape[0] > 0:
            if self.allFeatures.shape[0] == S2All.shape[0]:
                self.allFeatures = np.concatenate((self.allFeatures, S2All), axis=1)
            else:
                self.allFeatures = S2All
        trainingData = {'ids': self.ids, 'classNums': self.classNumbers, 'featuresValues': self.allFeatures}
        return trainingData

    def saveFeaturesNames(self):
        a=3

    def deleteLackData(self):
        self.currentDeleted = 0
        indexesForDelete = []
        for r in range(self.ids.shape[0]):
            sh = self.ids.shape
            if len(self.averagesS2.shape) > 1 and self.averagesS2.shape[1] > 0:
                eVS2 = self.averagesS2[r, 2]
                if eVS2 == 0:
                    indexesForDelete.append(r)
            if len(self.averagesS1.shape) > 1 and self.averagesS1.shape[1] > 0:
                eVS1 = self.averagesS1[r, 2]
                if eVS1 == 0:
                    indexesForDelete.append(r)
        self.deleteObject(indexesForDelete)

    def deleteWrongSeasonData(self):
        self.currentDeleted = 0
        conditionsFeatures = []  # 0:season[w,s], 1:featureName, 2:sign ('<','>'), 3: threshold
        conditionsFeatures.append(('w', 't#10_H', '<', 0.22))
        conditionsFeatures.append(('w', 't#9_H', '<', 0.22))
        conditionsFeatures.append(('w', 't#8_H', '<', 0.18))
        conditionsFeatures.append(('w', 't#7_H', '<', 0.2))
        conditionsFeatures.append(('w', 't#6_H', '<', 0.15))
        conditionsFeatures.append(('w', 't#5_H', '<', 0.15))
        conditionsFeatures.append(('w', 't#4_H', '<', 0.14))
        conditionsFeatures.append(('w', 't#10_A', '<', 12))
        conditionsFeatures.append(('w', 't#9_A', '<', 12))
        conditionsFeatures.append(('w', 't#8_A', '<', 11))
        conditionsFeatures.append(('w', 't#7_A', '<', 9))
        conditionsFeatures.append(('w', 't#6_A', '<', 7))
        conditionsFeatures.append(('w', 't#5_A', '<', 7.5))
        conditionsFeatures.append(('w', 't#4_A', '<', 8))

        conditionsFeatures.append(('s', 't#1_A', '>', 13))
        conditionsFeatures.append(('s', 't#2_A', '>', 11.8))
        conditionsFeatures.append(('s', 't#3_A', '>', 14))
        conditionsFeatures.append(('s', 't#4_A', '>', 13))
        conditionsFeatures.append(('s', 't#1_H', '>', 0.24))
        conditionsFeatures.append(('s', 't#2_H', '>', 0.25))
        conditionsFeatures.append(('s', 't#3_H', '>', 0.27))
        conditionsFeatures.append(('s', 't#4_H', '>', 0.26))

        springClassNumbers = [4, 6, 7, 10, 11, 13]
        winterClassNumbers = [5, 12, 14, 23]

        indexesForDelete = []

        for condition in conditionsFeatures:
            conditionSeason = condition[0]
            conditionFeatureName = condition[1]
            conditionSign = condition[2]
            conditionFeatureThr = condition[3]

            featureNameIndex = self.getIndexByFeatureNameS1(conditionFeatureName)
            for r in range(self.ids.shape[0]):
                sh = self.ids.shape
                rDeleteIndex = r - self.currentDeleted  # index updated with number of previous deleted objects
                if rDeleteIndex >= sh[0]:
                    break
                value = self.averagesS1[rDeleteIndex, featureNameIndex]
                classNumber = self.classNumbers[rDeleteIndex] + 1
                if self.checkCondition(value, conditionSign, conditionFeatureThr):
                    if (classNumber in winterClassNumbers and conditionSeason == 'w') or (
                            classNumber in springClassNumbers and conditionSeason == 's'):
                        indexesForDelete.append(rDeleteIndex)
        self.deleteObject(indexesForDelete)

    def getSecondSeasonByClassNumber(self, classNumber):
        springWinterPairs = [(4, 5), (11, 12), (13, 14), (15, 16)]
        returnClass = -1
        for i in range(len(springWinterPairs)):
            if springWinterPairs[i][0] == classNumber:
                returnClass = springWinterPairs[i][1]
            if springWinterPairs[i][1] == classNumber:
                returnClass = springWinterPairs[i][0]
        return returnClass

    def getIndexByFeatureNameS1(self, featureName):
        for nS1 in range(len(self.namesAveragesS1)):
            if self.namesAveragesS1[nS1] == featureName:
                return nS1
        return -1

    def checkCondition(self, value, sign, threshold):
        if sign == '>':
            if value > threshold:
                return True
        if sign == '<':
            if value < threshold:
                return True
        return False

    def deleteObject(self, objIndex):
        if len(self.averagesS2) > 0:
            self.averagesS2 = np.delete(self.averagesS2, objIndex, axis=0)
        if len(self.averagesS1) > 0:
            self.averagesS1 = np.delete(self.averagesS1, objIndex, axis=0)
        self.ids = np.delete(self.ids, objIndex, axis=0)
        self.classNumbers = np.delete(self.classNumbers, objIndex, axis=0)
        self.currentDeleted = self.currentDeleted + 1

    def changeClassNums(self):
        self.classNumbers[self.classNumbers > 1] = 0
        indexes0 = np.argwhere(self.classNumbers == 0)
        indexes1 = np.argwhere(self.classNumbers == 1)
        countToDelete = len(self.classNumbers - len(indexes1))
        randIndexesToDelete = (np.random.rand(countToDelete)*countToDelete).astype(int)
        self.deleteObject(randIndexesToDelete)

    def GetTrainingDataFromObjects(self, objects, type, selectedFeatures):
        numObjects = len(objects)
        featuresCount = len(self.GetSelectedFeatures(objects[0], type, selectedFeatures))
        featuresValues = np.zeros((numObjects, featuresCount), dtype=np.float32)
        classesNums = np.zeros(numObjects, dtype=np.int)
        index = 0
        for o in objects:
            featuresValues[index, :] = self.GetSelectedFeatures(o, type, selectedFeatures)
            classesNums[index] = o.intclass
            index += 1
        self.numbersOfTerms = len(objects[0].features) / 6
        trainingData = {'classNums': classesNums, 'featuresValues': featuresValues}
        return trainingData

    def reduceNumberOfReferenceData(self, maxNumberOfObjects):
        allClasses = np.unique(self.classNumbers)
        numOfAllClasses = len(allClasses)
        numOfAllTrainingObjects = len(self.classNumbers)

        if numOfAllClasses != len(maxNumberOfObjects):
            print('Reduction is not possible.')
            return
        print("Class counts after reduction:")
        indexesForDelete = []
        for c in range(numOfAllClasses):
            maxNum = maxNumberOfObjects[c]
            clIndexes = []
            for i in range(numOfAllTrainingObjects):
                if self.classNumbers[i] == c:
                    clIndexes.append(i)
            if len(clIndexes) > maxNum:
                delIndexesCount = len(clIndexes) - maxNum
                indexesForDeleteClass = random.sample(clIndexes, delIndexesCount)
                for icd in indexesForDeleteClass:
                    indexesForDelete.append(icd)
        self.deleteObject(indexesForDelete)
        self.printClassStats()

    def reduceNumberOfReferenceDataStatic(self, trainingData, maxNumberOfObjects):
        classNumbers = trainingData['classNums']

        allClasses = np.unique(classNumbers)
        numOfAllClasses = len(allClasses)
        featuresValues = trainingData['featuresValues']
        ids = trainingData['ids']
        selectedIndexes = []

        if numOfAllClasses != len(maxNumberOfObjects):
            print('Reduction is not possible.')
            return

        for c in range(numOfAllClasses):
            cl = allClasses[c]
            classCounter = 0
            maxNum = maxNumberOfObjects[c]
            clIndexes = []
            numOfAllTrainingObjects = len(classNumbers)
            for i in range(numOfAllTrainingObjects):
                if classNumbers[i] == c:
                    clIndexes.append(i)
            if len(clIndexes) > maxNum:
                clIndexes = random.sample(clIndexes, maxNum)
            selectedIndexes.extend(clIndexes)
        selectedClassNumbers = classNumbers[selectedIndexes]
        selectedFeatures = featuresValues[selectedIndexes, :]
        ids = ids[selectedIndexes]
        trainingData = {'ids': ids, 'classNums': selectedClassNumbers, 'featuresValues': selectedFeatures}
        # self.printClassStats(selectedClassNumbers)
        return trainingData