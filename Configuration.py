import os.path
from pathlib import Path


class Configuration:
    def __init__(self, confFile):
        self.passNumber = 0
        self.trainingPointsShapefile = ''
        self.trainingClassesColumnName = ''
        self.classesList = []
        self.workingDir = ''
        self.S1ProcessedDir = ''
        self.S2ProcessedDir = ''
        self.segmentationTiffFile = ''
        self.statsDir = ''
        self.prepareProgramExePath = ''
        self.AllS1 = True
        self.AllS2 = True
        self.RefS1 = True
        self.RefS2 = True
        self.overwrite = True
        self.loadArgsFromFile(confFile)
        self.prepareEnv()

    def loadArgsFromFile(self, confFile):
        with open(confFile) as f:
            content = f.readlines()
        # remove whitespace characters like `\n` at the end of each line and " if occurs
        args = [x.strip().replace('"', '') for x in content]
        self.passNumber = int(args[0])
        self.trainingPointsShapefile = args[1]
        self.trainingClassesColumnName = args[2]
        commaSeparatedClasses = args[3]
        self.classesList = commaSeparatedClasses.split(',')
        self.workingDir = args[4]
        self.S1ProcessedDir = args[5]
        self.S2ProcessedDir = args[6]
        self.segmentationTiffFile = args[7]
        if len(args) > 8:
            self.AllS1 = False
            self.AllS2 = False
            self.RefS1 = False
            self.RefS2 = False
            lowerStr = args[8].lower()
            if 'alls1' in lowerStr:
                self.AllS1 = True
            if 'alls2' in lowerStr:
                self.AllS2 = True
            if 'refs1' in lowerStr:
                self.RefS1 = True
            if 'refs2' in lowerStr:
                self.RefS2 = True
        if len(args) > 9:
            lowerStr = args[9].lower()
            if 'overwrite=false' in lowerStr:
                self.overwrite = False
            if 'overwrite=true' in lowerStr:
                self.overwrite = True

        #todo: add check segmentation resolution and crop to other data if needed
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'S1prepareForClassificationP.exe')
        self.prepareProgramExePath = filename

    def makeDirIfNotExists(self, newDirPath):
        if not os.path.exists(newDirPath):
            os.makedirs(newDirPath)

    def prepareEnv(self):
        self.makeDirIfNotExists(self.workingDir)
        self.makeDirIfNotExists(self.S1ProcessedDir)
        self.makeDirIfNotExists(self.S2ProcessedDir)
        self.statsDir = os.path.join(self.workingDir,  'P'+str(self.passNumber), 'statsT3')
        self.makeDirIfNotExists(self.statsDir)

    def getS1TimesDirs(self):
        pdir = Path(self.S1ProcessedDir, 'P' + str(self.passNumber), 'mozaika')
        if not pdir.is_dir():
            pdir = Path(self.S1ProcessedDir, 'P' + str(self.passNumber))
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
        return dir_list

    def getS2TimesDirs(self):
        pdir = Path(self.S2ProcessedDir, 'P' + str(self.passNumber), 'mozaika')
        if not pdir.is_dir():
            pdir = Path(self.S2ProcessedDir, 'P' + str(self.passNumber))
        dir_list = []
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
        return dir_list
