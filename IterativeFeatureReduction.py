import csv
import math
import time

import InfoPrinter
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from pathlib import Path
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from Configuration import Configuration


class IterativeFeatureReduction:
    def __init__(self, conf: Configuration):
        self.conf = conf
        self.referenceData = []
        self.indexesOfSelectedFeatures = []
        self.cutFeaturePercentInIteration = 0.05
        self.minFeaturesCount = 80
        self.foldCut = 0.2
        self.resultsSaveDirectory = conf.statsDir

    def removeByImportances(self, importances, features, featuresIndexes, lenOfCut):
        sortedFeaturesIndexes = sorted(range(len(importances)), key=lambda k: importances[k])
        selectedFeaturesIndexes = sortedFeaturesIndexes[0:lenOfCut]
        sortedSelectedFeatures = sorted(selectedFeaturesIndexes)

        featuresValues = np.delete(features, sortedSelectedFeatures, axis=1)
        featuresIndexes = np.delete(featuresIndexes, sortedSelectedFeatures)

        featuresValuesAndIndexes = {'featuresValues': featuresValues, 'featuresIndexes': featuresIndexes}
        return featuresValuesAndIndexes

    def PerformSeparateS1S2FeatReductionTest(self, S1ObjectStats, S2ObjectStats):
        classNumbers = S1ObjectStats['classNums']
        S1Features = S1ObjectStats['featuresValues']
        S2Features = S2ObjectStats['featuresValues']
        ids = S1ObjectStats['ids']
        maxOA = 0#max of mean OA from S1 and S2 classifications
        maxS1proba = []
        maxS2proba = []
        maxS1Classes = []
        maxS2Classes = []
        attempts = 1
        fvS1Copy = S1Features
        fvS2Copy = S2Features
        featuresIndexesS1 = range(len(S1Features[0]))
        featuresIndexesS2 = range(len(S2Features[0]))
        maxDepthSet = [100]
        nEstimatorsSet = [1000]
        for maxDepth in maxDepthSet:
            for nEstimators in nEstimatorsSet:
                oaChain = []
                featuresS1Values = fvS1Copy
                featuresS2Values = fvS2Copy
                while featuresS1Values.shape[1] > self.minFeaturesCount and featuresS2Values.shape[1] > self.minFeaturesCount:
                    newCutS1 = math.ceil(featuresS1Values.shape[1] * self.cutFeaturePercentInIteration)
                    newCutS2 = math.ceil(featuresS2Values.shape[1] * self.cutFeaturePercentInIteration)
                    print("Odciecie S1: " + str(newCutS1) + "   |   S2: " + str(newCutS2))
                    printTxt = "Features:   " + str(featuresS1Values.shape[1]) + "   |   " + str(featuresS2Values.shape[1])
                    sumImportancesS1 = np.zeros((len(featuresS1Values[0])))
                    sumImportancesS2 = np.zeros((len(featuresS2Values[0])))
                    sumOA = 0
                    for t in range(attempts):
                        X_indexes = range(len(classNumbers))
                        y_train = classNumbers
                        X_indexesTrain, X_indexesTest, y_train, y_test = train_test_split(X_indexes, y_train, test_size=self.foldCut)
                        X_trainS1 = featuresS1Values[X_indexesTrain]
                        X_testS1 = featuresS1Values[X_indexesTest]
                        X_trainS2 = featuresS2Values[X_indexesTrain]
                        X_testS2 = featuresS2Values[X_indexesTest]
                        idsTest = ids[X_indexesTest]

                        model1 = RandomForestClassifier(max_depth=maxDepth, n_estimators=nEstimators, n_jobs=6)
                        model2 = RandomForestClassifier(max_depth=maxDepth, n_estimators=nEstimators, n_jobs=6)

                        model1.fit(X_trainS1, y_train)
                        y_predS1 = model1.predict(X_testS1)
                        S1predProba = model1.predict_proba(X_testS1)

                        oaS1 = accuracy_score(y_test, y_predS1)
                        sumOA = sumOA + oaS1
                        importancesS1 = model1.feature_importances_
                        sumImportancesS1 = np.sum([sumImportancesS1, importancesS1], axis=0)

                        model2.fit(X_trainS2, y_train)
                        y_predS2 = model2.predict(X_testS2)
                        S2predProba = model2.predict_proba(X_testS2)

                        oaS2 = accuracy_score(y_test, y_predS2)
                        sumOA = sumOA + oaS2
                        importancesS2 = model2.feature_importances_
                        sumImportancesS2 = np.sum([sumImportancesS2, importancesS2], axis=0)

                        meanOA = (oaS1 + oaS2)/2
                        resultLine = "S1OA: " + str(oaS1) + "   |   S2OA: " + str(oaS2) + "   |   mean: " + str(meanOA)
                        print(resultLine)

                    meanGeneralOA = sumOA / (attempts * 2)
                    oaChain.append(meanGeneralOA)
                    printTxt = printTxt + '  ' + str(meanGeneralOA * 100) + "%"
                    print(printTxt)

                    if meanOA > maxOA:
                        maxOA = meanOA
                        maxS1proba = S1predProba
                        maxS2proba = S2predProba
                        maxS1Classes = y_predS1
                        maxS2Classes = y_predS2
                        maxIds = idsTest
                        maxValidClasses = y_test

                        self.saveSeparatedS1S2results(maxS1proba, maxS2proba, maxS1Classes, maxS2Classes, idsTest, y_test)
                        # self.saveClassifier()

                    featuresValuesAndIndexesS1 = self.removeByImportances(importancesS1, featuresS1Values, featuresIndexesS1, newCutS1)
                    featuresS1Values = featuresValuesAndIndexesS1['featuresValues']
                    featuresIndexesS1 = featuresValuesAndIndexesS1['featuresIndexes']

                    featuresValuesAndIndexesS2 = self.removeByImportances(importancesS2, featuresS2Values, featuresIndexesS2, newCutS2)
                    featuresS2Values = featuresValuesAndIndexesS2['featuresValues']
                    featuresIndexesS2 = featuresValuesAndIndexesS2['featuresIndexes']

        self.saveSeparatedS1S2results(maxS1proba, maxS2proba, maxS1Classes, maxS2Classes, maxIds, maxValidClasses)

    def saveSeparatedS1S2results(self, maxS1proba, maxS2proba, maxS1Classes, maxS2Classes, idsTest, validClasses):
        maxMaxS1proba = np.amax(maxS1proba, 1)
        maxMaxS2proba = np.amax(maxS2proba, 1)
        with open(self.resultsSaveDirectory + "/" + "testSeparatedS1S2" + ".csv", "w", newline='') as my_csv:
            for i in range(len(maxS1proba)):
                lineTxt = ""
                lineTxt = lineTxt + str(idsTest[i]) + ';'
                lineTxt = lineTxt + str(validClasses[i]) + ';'
                lineTxt = lineTxt + str(maxS1Classes[i]) + ';'
                lineTxt = lineTxt + str(maxMaxS1proba[i]) + ';'
                lineTxt = lineTxt + str(maxS2Classes[i]) + ';'
                lineTxt = lineTxt + str(maxMaxS2proba[i]) + ';'
                lineTxt = lineTxt + "\n"

                my_csv.write(lineTxt)

    def saveErrorMatrix(self, errorMatrix):
        clNames = []
        clNames = self.conf.confArgs.classesToClassify

        EMfilepath = self.conf.fMaxErrorMatrix
        printer = InfoPrinter.InfoPrinter(output_file=EMfilepath, class_names=clNames, conf_matrix=errorMatrix)
        printer.create_xlsx_file_with_default_values()

    def saveClassifier(self, model, featureIndexes):
        modelFilePath = self.conf.fMaxModel
        featureIndexesFilePath = self.conf.fMaxFeatures
        joblib.dump(model, modelFilePath)
        joblib.dump(featureIndexes, featureIndexesFilePath)

    def testManyClassifiers(self, X_train, X_test, y_train, y_test):
        names = ["Nearest Neighbors", "Linear SVM", "RBF SVM",
                 "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
                 "Naive Bayes", "QDA"]
        classifiers = [
            KNeighborsClassifier(3),
            SVC(kernel="linear", C=0.025),
            SVC(gamma=2, C=1),
            DecisionTreeClassifier(max_depth=5),
            RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
            MLPClassifier(alpha=1, max_iter=1000),
            AdaBoostClassifier(),
            GaussianNB(),
            QuadraticDiscriminantAnalysis()]
        for name, clf in zip(names, classifiers):
            now = time.time()
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            oa = accuracy_score(y_test, y_pred)
            later = time.time()
            difference = int(later - now)
            txt = name + '  OA: ' + str(oa) + '    time: ' + str(difference) + 's'
            print(txt)

    def PerformIterativeFeatureReductionTest(self, objectsStats):
        self.referenceData = objectsStats
        classNumbers = self.referenceData['classNums']
        featuresValues = self.referenceData['featuresValues']
        maxFeaturesVector = []
        maxOA = 0
        attempts = 1

        featureScores = self.createEmptyFeatureScoresMatrix(featuresValues)
        featuresIndexes = np.arange(len(featuresValues[0]))
        fvCopy = featuresValues
        maxDepth = self.conf.confArgs.optionClassifierMaxDepth
        nEstimators = self.conf.confArgs.optionClassifierNEstimators
        njobs = self.conf.confArgs.optionNJobs

        oaChain = []
        featuresValues = fvCopy
        countOfFeaturesSet = []
        featureTestIterator = 0
        while featuresValues.shape[1] > self.minFeaturesCount:
            countOfFeaturesSet.append(featuresValues.shape[1])
            newCut = math.ceil(featuresValues.shape[1] * self.cutFeaturePercentInIteration)
            lenOfCut = newCut
            print("Odciecie: " + str(lenOfCut))
            printTxt = str(featuresValues.shape[1])
            resultLine = 'scikit;' + str(maxDepth) + ';' + str(nEstimators) + ';' + str(featuresValues.shape[1] - 1)
            sumImportances = np.zeros((len(featuresValues[0])))
            sumOA = 0
            sumOAcv = 0
            for t in range(0, attempts):
                X_train = featuresValues
                y_train = classNumbers
                X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=self.foldCut)
                # self.testManyClassifiers(X_train, X_test, y_train, y_test)

                model = RandomForestClassifier(max_depth=maxDepth, n_estimators=nEstimators, n_jobs=njobs)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                oa = accuracy_score(y_test, y_pred)
                sumOA = sumOA + oa
                importances = model.feature_importances_
                sumImportances = np.sum([sumImportances, importances], axis=0)
                resultLine = resultLine + ';' + str(oa)

            meanOA = sumOA / attempts
            oaChain.append(meanOA)
            printTxt = printTxt + '  ' + str(meanOA * 100) + "%     CV: " + str(sumOAcv * 10) + '%'
            print(printTxt)

            # odcinanie najgorszych warstw
            for importanceIndex in range(len(featuresIndexes)):
                featureIndex = featuresIndexes[importanceIndex]
                featureScores[featureIndex, featureTestIterator] = importances[importanceIndex]

            sortedFeaturesIndexes = sorted(range(len(importances)), key=lambda k: importances[k])
            selectedFeaturesIndexes = sortedFeaturesIndexes[0:lenOfCut]
            sortedSelectedFeatures = sorted(selectedFeaturesIndexes)

            if meanOA >= maxOA:
                maxOA = meanOA
                maxEM = confusion_matrix(y_test, y_pred)
                maxFeaturesVector = featuresIndexes
                maxModel = model
                self.saveErrorMatrix(maxEM)
                self.saveClassifier(maxModel, maxFeaturesVector)

            featuresValues = np.delete(featuresValues, sortedSelectedFeatures, axis=1)
            featuresIndexes = np.delete(featuresIndexes, sortedSelectedFeatures)
            featureTestIterator = featureTestIterator + 1

        with open(Path(self.resultsSaveDirectory, "importances" + ".csv"), "w+", newline='') as my_csv:
            csvWriter = csv.writer(my_csv, delimiter=';')
            csvWriter.writerows(featureScores)
        # return the best X indexes

        self.indexesOfSelectedFeatures = maxFeaturesVector
        print("####MAX: " + str(maxOA))
        self.saveErrorMatrix(maxEM)
        return maxFeaturesVector

    def createEmptyFeatureScoresMatrix(self):
        return self.createEmptyFeatureScoresMatrix(self.referenceData['featuresValues'])

    def createEmptyFeatureScoresMatrix(self, featureValues):
        featureScoreWidth = 0
        featuresCountTest = featureValues.shape[1]
        featuresCountSet = []
        while featuresCountTest > self.minFeaturesCount:
            featuresCountSet.append(featuresCountTest)
            newCut = math.ceil(featuresCountTest * self.cutFeaturePercentInIteration)
            featuresCountTest = featuresCountTest - newCut
            featureScoreWidth = featureScoreWidth + 1

        featureScores = np.zeros((featureValues.shape[1], featureScoreWidth))
        return featureScores
