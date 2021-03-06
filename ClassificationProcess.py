import os
from pathlib import Path
from Configuration import Configuration
from FeaturesMangerS1S2 import FeaturesMangerS1S2
from FullImageClassification import FullImageClassification
from IterativeFeatureReduction import IterativeFeatureReduction


def runSystemProcess(command):
    # if not self.outputCommandsFileHandle.closed:
    #     self.outputCommandsFileHandle.write(command)
    #     self.outputCommandsFileHandle.write('\n')
    # print('\n' + command)
    os.system(command)


class ClassificationProcess:
    """
    Preparing, running and postprocessing of classification process.
    """

    def __init__(self, conf: Configuration):
        self.configuration = conf
        self.refStatsDir = ''
        self.allStatsDir = ''
        self.resultDir = ''

        self.csvTrainingS1 = ''
        self.csvTrainingS2 = ''
        self.features = None

        self.refStatsDir = self.configuration.statsDir
        self.allStatsDir = self.configuration.statsDir
        self.resultDir = self.configuration.statsDir
        self.csvTrainingS1 = self.configuration.fCsvRefStatsS1FilePath
        self.csvTrainingS2 = self.configuration.fCsvRefStatsS2FilePath

    def prepareTraining(self):
        print("Classification: preparing input training data.")
        fm = FeaturesMangerS1S2()
        if self.csvTrainingS1.exists():
            fm.readRefS1DataFromCSV(self.csvTrainingS1)
        if self.csvTrainingS2.exists():
            fm.readRefS2DataFromCSV(self.csvTrainingS2)
        fm.deleteWrongData()
        if len(self.configuration.confArgs.optionStratificationCounts) > 0:
            if len(self.configuration.confArgs.optionStratificationCounts) == len(self.configuration.confArgs.classesToClassify):
                fm.reduceNumberOfReferenceData(self.configuration.confArgs.optionStratificationCounts)
            else:
                print('#Wrong counts of optionStratificationCounts and classesToClassify.')
        fm.printClassStats()
        self.features = fm.getAllFeatures()
        fm.saveFeaturesNames()

    @staticmethod
    def saveTxtClassesToRaster(configuration: Configuration):
        if configuration.confArgs.overwrite or not configuration.fResultClassesTifFile.exists():
            command = str(configuration.prepareProgramExePath)
            command = command + ' paint ' + str(configuration.fWorkingRasterSegmentation) \
                      + ' ' + str(configuration.fBinCoordFilePath) \
                      + ' ' + str(configuration.fResultClassesTxtFile) \
                      + ' ' + str(configuration.fResultClassesTifFile)
            if Path(configuration.fWorkingRasterSegmentation).exists() and Path(configuration.fBinCoordFilePath).exists() and Path(configuration.fResultClassesTxtFile).exists():
                runSystemProcess(command)
                print("Classification: saving results to to file " + str(configuration.fResultClassesTifFile))

    @staticmethod
    def saveTxtProbabilityToRaster(configuration: Configuration):
        if configuration.confArgs.overwrite or not configuration.fResultProbabilityTifFile.exists():
            command = str(configuration.prepareProgramExePath)
            command = command + ' paint ' + str(configuration.fWorkingRasterSegmentation) \
                      + ' ' + str(configuration.fBinCoordFilePath) \
                      + ' ' + str(configuration.fResultProbability256TxtFile) \
                      + ' ' + str(configuration.fResultProbabilityTifFile)
            if Path(configuration.fWorkingRasterSegmentation).exists() and Path(configuration.fBinCoordFilePath).exists() and Path(configuration.fResultProbability256TxtFile).exists():
                runSystemProcess(command)

    @staticmethod
    def saveClassificationToRaster(configuration: Configuration):
        ClassificationProcess.saveTxtClassesToRaster(configuration)
        ClassificationProcess.saveTxtProbabilityToRaster(configuration)

    def doClassificationForAllObjects(self):
        print("Classification: iterative training.")
        trainingClassifier = IterativeFeatureReduction(self.configuration)
        trainingClassifier.PerformIterativeFeatureReductionTest(self.features)
        print("Classification: full image classification.")
        fimc = FullImageClassification(self.configuration)
        fimc.Classify()
        self.saveClassificationToRaster(self.configuration)
