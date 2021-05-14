from Configuration import Configuration
import joblib
import StatsReader
from pathlib import Path
import FeaturesMangerS1S2
import numpy as np

class FullImageClassification:
    resultsSaveDir = ''
    statsDir = ''
    inputModel = None
    inputFeaturesIndexes = []
    outputIdsFilePath = ''
    inputAllStatsS1FilePath = ''
    inputAllStatsS2FilePath = ''
    binReader = None
    allObjectsS1Matrix = []
    allObjectsS2Matrix = []

    def __init__(self, conf: Configuration):
        self.conf = conf
        self.statsDir = self.conf.statsDir
        self.resultsSaveDir = self.statsDir
        self.inputAllStatsS1FilePath = self.conf.fBinAllStatsS1FilePath
        self.inputAllStatsS2FilePath = self.conf.fBinAllStatsS2FilePath
        self.binReader = StatsReader.StatsReader()

        if self.inputAllStatsS1FilePath.exists():
            self.allObjectsS1Matrix = self.binReader.readFromBinFileAsPdDataFrame(self.inputAllStatsS1FilePath)
            s1ObjNumber = self.allObjectsS1Matrix.shape[0]
            print(str(s1ObjNumber) + " objects loaded with " + str(self.allObjectsS1Matrix.shape[1] - 2) + " S1 basic features.")

        if self.inputAllStatsS2FilePath.exists():
            self.allObjectsS2Matrix = self.binReader.readFromBinFileAsPdDataFrame(self.inputAllStatsS2FilePath)
            s2ObjNumber = self.allObjectsS2Matrix.shape[0]
            print(str(s2ObjNumber) + " objects loaded with " + str(self.allObjectsS2Matrix.shape[1]-2) + " S2 basic features.")

        self.LoadClassifier()

    def LoadClassifier(self):
        modelFilePath = self.conf.fMaxModel
        featureIndexes = self.conf.fMaxFeatures
        self.inputModel = joblib.load(modelFilePath)
        self.inputFeaturesIndexes = joblib.load(featureIndexes)

    def getObjectsNumber(self):
        if len(self.allObjectsS1Matrix) > 0 and self.allObjectsS1Matrix.shape[0] > 0:
            return self.allObjectsS1Matrix.shape[0]
        if len(self.allObjectsS2Matrix) > 0 and self.allObjectsS2Matrix.shape[0] > 0:
            return self.allObjectsS2Matrix.shape[0]
        return 0

    def Classify(self):
        objNumber = self.getObjectsNumber()
        resultClasses = np.zeros(objNumber, dtype=int)
        resultIds = np.zeros(objNumber, dtype=int)
        resultProbability = np.zeros(objNumber)
        percentPart = int(objNumber / 100)
        fm = FeaturesMangerS1S2.FeaturesMangerS1S2()
        percentDisp = 0
        for down in range(0, objNumber, percentPart):
            if percentDisp == 100:
                a=3
            up = down + percentPart
            if up > objNumber:
                up = objNumber
            objsPartS1 = self.allObjectsS1Matrix[down:up:]
            objsPartS2 = self.allObjectsS2Matrix[down:up:]
            fm.readS1DataFromDataFrame(objsPartS1)
            fm.readS2DataFromDataFrame(objsPartS2)
            classificationData = fm.getAllFeatures(False)
            features = classificationData['featuresValues']
            featuresSelected = features[:, self.inputFeaturesIndexes]
            ids = classificationData['ids']

            cl = self.inputModel.predict(featuresSelected)
            pr = self.inputModel.predict_proba(featuresSelected)
            prMax = np.amax(pr, 1)
            resultClasses[down:up] = cl
            resultProbability[down:up] = prMax
            resultIds[down:up] = ids
            print(str(percentDisp) + '%')
            percentDisp = percentDisp + 1
        resultClassesFilePath = self.conf.fResultClassesTxtFile
        idFilePath = self.conf.fResultIdTxtFile
        probaFilePath = self.conf.fResultProbabilityTxtFile
        np.savetxt(resultClassesFilePath, resultClasses, '%d')
        np.savetxt(probaFilePath, resultProbability, '%f')
        np.savetxt(idFilePath, resultIds, '%d')
        print(type(resultProbability))
        resultProbability256 = (np.array(resultProbability) * 255).astype(int)
        proba256FilePath = self.conf.fResultProbability256TxtFile
        np.savetxt(proba256FilePath, resultProbability256, '%f')

