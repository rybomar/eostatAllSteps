import os.path
from pathlib import Path
import json


class ConfigurationArgs:
    def __init__(self, jsonFile=''):
        self.orbitNumber = 0#from 1 to 6 (for Poland from west to east)
        self.trainingPointsShapefile = ''#path to .shp file
        self.trainingColumnInShapefile = ''#column's name in .shp file with class names
        self.workingDir = ''#path to directory to store temporary data
        self.S1DataMainDir = ''#path where S1 data(prepared with MTSAR) are stored
        self.S2DataMainDir = ''#path where S2 data(prepared with filled gaps) are stored
        self.segmentationRasterFile = ''#path to raster file with segmentation (or parcels)
        self.overwrite = True#boolean
        #optional:
        self.options = []#list with possible options AllS1, AllS2, RefS1, RefS2
        self.classesToClassify = []#list with strings (names of classes), eg. ['pszenica', 'burak']
        self.optionStratificationCounts = []#list with ints, corresponds to optionSelectedClasses
        #optionalClassifier:
        self.optionClassifierMaxDepth = 100
        self.optionClassifierNEstimators = 10000
        self.optionNJobs = 4

        if len(jsonFile) > 0:
            self.loadFromJSON(jsonFile)

    def loadFromJSON(self, jsonFile):
        with open(jsonFile) as f:
            args = json.load(f)
            self.orbitNumber = int(args['orbitNumber'])
            self.trainingPointsShapefile = args['trainingPointsShapefile']
            self.trainingColumnInShapefile = args['trainingColumnInShapefile']
            self.workingDir = args['workingDir']
            self.S1DataMainDir = args['S1DataMainDir']
            self.S2DataMainDir = args['S2DataMainDir']
            self.segmentationRasterFile = args['segmentationRasterFile']
            self.options = args['options']
            self.classesToClassify = args['classesToClassify']
            self.optionStratificationCounts = args['optionStratificationCounts']
            self.optionClassifierMaxDepth = args['optionClassifierMaxDepth']
            self.optionClassifierNEstimators = args['optionClassifierNEstimators']
            self.optionNJobs = args['optionNJobs']
            self.overwrite = args['overwrite']

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def saveJSON(self, filePath='configuration.json'):
        with open(filePath, 'w') as file:
            file.write(self.toJSON())



class Configuration:
    def __init__(self, confFile):
        # todo: add check segmentation resolution and crop to other data if needed
        self.confArgs = ConfigurationArgs(confFile)
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'S1prepareForClassificationP.exe')
        self.prepareProgramExePath = filename
        self.overwrite = self.confArgs.overwrite
        self.AllS1 = True
        self.AllS2 = True
        self.RefS1 = True
        self.RefS2 = True
        if(len(self.confArgs.options) > 0):
            self.AllS1 = False
            self.AllS2 = False
            self.RefS1 = False
            self.RefS2 = False
            for o in self.confArgs.options:
                lowerStr = str(o).lower()
                if 'alls1' in lowerStr:
                    self.AllS1 = True
                if 'alls2' in lowerStr:
                    self.AllS2 = True
                if 'refs1' in lowerStr:
                    self.RefS1 = True
                if 'refs2' in lowerStr:
                    self.RefS2 = True
        self.orbitWorkingDir = ''
        self.statsDir = ''
        self.segmentationRasterFile = ''
        self.fResultClassesTxtFile = ''
        self.fResultClassesTifFile = ''
        self.fResultProbabilityTxtFile = ''
        self.fResultProbabilityTifFile = ''
        self.fResultIdTxtFile = ''
        self.fResultProbability256TxtFile = ''

        self.fWorkingTrainingPointsShapefile = ''
        self.fWorkingRasterSegmentation = ''
        self.fWorkingRasterTrainingPoints = ''
        self.fOutputCommandsFilePath = ''
        self.fBinCoordFilePath = ''
        self.fBinRefCoordFilePath = ''
        self.fBinAllStatsS1FilePath = ''
        self.fBinRefStatsS1FilePath = ''
        self.fCsvRefStatsS1FilePath = ''
        self.fBinAllStatsS2FilePath = ''
        self.fBinRefStatsS2FilePath = ''
        self.fCsvRefStatsS2FilePath = ''

        self.fMaxModel = ''
        self.fMaxErrorMatrix = ''
        self.fMaxFeatures = ''

        self.generatePaths()
        self.prepareEnv()

    def generatePaths(self):
        self.orbitWorkingDir = Path(self.confArgs.workingDir, 'P' + str(self.confArgs.orbitNumber))
        self.statsDir = Path(self.orbitWorkingDir, 'stats')
        self.segmentationRasterFile = self.confArgs.segmentationRasterFile
        self.fResultClassesTxtFile = Path(self.statsDir, 'resultClasses.txt')
        self.fResultClassesTifFile = Path(self.statsDir, 'resultClasses.tif')
        self.fResultProbabilityTxtFile = Path(self.statsDir, 'resultProbability.txt')
        self.fResultProbabilityTifFile = Path(self.statsDir, 'resultProbability.tif')
        self.fResultIdTxtFile = Path(self.statsDir, 'resultIds.txt')
        self.fResultProbability256TxtFile = Path(self.statsDir, 'resultProbability256.txt')

        self.fWorkingTrainingPointsShapefile = Path(self.statsDir, 'trainingShp.shp')
        self.fWorkingRasterSegmentation = Path(self.statsDir, 'segments.tif')
        self.fWorkingRasterTrainingPoints = Path(self.statsDir, 'segmentsPointsSelected.tif')
        self.fOutputCommandsFilePath = Path(self.statsDir, 'commands.txt')
        self.fBinCoordFilePath = Path(self.statsDir, 'allCoords.bin')
        self.fBinRefCoordFilePath = Path(self.statsDir, 'RefCoordsSelected.bin')
        self.fBinAllStatsS1FilePath = Path(self.statsDir, 'allStatsS1.bin')
        self.fBinRefStatsS1FilePath = Path(self.statsDir, 'refStatsS1.bin')
        self.fCsvRefStatsS1FilePath = Path(self.statsDir, 'refStatsS1.csv')
        self.fBinAllStatsS2FilePath = Path(self.statsDir, 'allStatsS2.bin')
        self.fBinRefStatsS2FilePath = Path(self.statsDir, 'refStatsS2.bin')
        self.fCsvRefStatsS2FilePath = Path(self.statsDir, 'refStatsS2.csv')

        self.fMaxModel = Path(self.statsDir, 'maxModel.bin')
        self.fMaxErrorMatrix = Path(self.statsDir, 'maxModel.xlsx')
        self.fMaxFeatures = Path(self.statsDir, 'maxFeatureIndexes.bin')


    def makeDirIfNotExists(self, newDirPath):
        if not os.path.exists(newDirPath):
            os.makedirs(newDirPath)

    def prepareEnv(self):
        self.makeDirIfNotExists(self.orbitWorkingDir)
        # self.makeDirIfNotExists(self.confArgs.S2DataMainDir)
        # self.makeDirIfNotExists(self.confArgs.S1DataMainDir)
        self.makeDirIfNotExists(self.statsDir)

    def getS1TimesDirs(self):
        pdir = Path(self.confArgs.S1DataMainDir, 'P' + str(self.confArgs.orbitNumber), 'mozaika')
        if not pdir.is_dir():
            pdir = Path(self.confArgs.S1DataMainDir, 'P' + str(self.confArgs.orbitNumber))
        if not pdir.is_dir():
            pdir = Path(self.confArgs.S1DataMainDir, 'mozaika')
        if not pdir.is_dir():
            pdir = Path(self.confArgs.S1DataMainDir)
        dir_list = []
        for x in pdir.iterdir():
            if x.is_dir():
                requiredFiles = []
                requiredFiles.append(Path(x, 'A.tif'))
                requiredFiles.append(Path(x, 'H.tif'))
                requiredFiles.append(Path(x, 'L1.tif'))
                requiredFiles.append(Path(x, 'T11Rlog.tif'))
                requiredFiles.append(Path(x, 'T12Rlog.tif'))
                requiredFiles.append(Path(x, 'T22Rlog.tif'))
                requiredFilesFound = 0
                for r in requiredFiles:
                    if r.is_file():
                        requiredFilesFound = requiredFilesFound + 1
                if requiredFilesFound == len(requiredFiles):
                    dir_list.append(x)
        return dir_list#debug [1:4]

    def getS2TimesDirs(self):
        pdir = Path(self.confArgs.S2DataMainDir, 'P' + str(self.confArgs.orbitNumber), 'mozaika')
        if not pdir.is_dir():
            pdir = Path(self.confArgs.S2DataMainDir, 'P' + str(self.confArgs.orbitNumber))
        dir_list = []
        if not pdir.is_dir():
            return dir_list
        for x in pdir.iterdir():
            if x.is_dir():
                requiredFiles = []
                requiredFiles.append(Path(x, 'B02.tif'))
                requiredFiles.append(Path(x, 'B03.tif'))
                requiredFiles.append(Path(x, 'B04.tif'))
                requiredFiles.append(Path(x, 'B05.tif'))
                requiredFiles.append(Path(x, 'B06.tif'))
                requiredFiles.append(Path(x, 'B07.tif'))
                requiredFiles.append(Path(x, 'B8A.tif'))
                requiredFiles.append(Path(x, 'B11.tif'))
                requiredFiles.append(Path(x, 'B12.tif'))
                requiredFilesFound = 0
                for r in requiredFiles:
                    if r.is_file():
                        requiredFilesFound = requiredFilesFound + 1
                if requiredFilesFound == len(requiredFiles):
                    dir_list.append(x)
        return dir_list#debug[1:4]
