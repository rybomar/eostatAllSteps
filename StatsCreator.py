import os
from pathlib import Path
from shutil import copy
from osgeo import gdal
from Configuration import Configuration


class StatsCreator:
    def __init__(self, conf: Configuration):
        self.outputCommandsFilePath = ''
        self.outputCommandsFileHandle = 0
        self.conf = conf
        self.statsDir = conf.statsDir
        self.trainingPointsShapefile = conf.fWorkingTrainingPointsShapefile
        self.segmentationTiffFile = conf.confArgs.segmentationRasterFile
        self.workingTrainingPointsShapefile = conf.fWorkingTrainingPointsShapefile
        self.workingRasterSegmentation = conf.fWorkingRasterSegmentation
        self.workingRasterTrainingPoints = conf.fWorkingRasterTrainingPoints
        self.outputCommandsFilePath = conf.fOutputCommandsFilePath
        # self.outputCommandsFileHandle = open(self.outputCommandsFilePath, "w")
        self.binCoordFilePath = conf.fBinCoordFilePath
        self.binRefCoordFilePath = conf.fBinRefCoordFilePath
        self.binAllStatsS1FilePath = conf.fBinAllStatsS1FilePath
        self.binRefStatsS1FilePath = conf.fBinRefStatsS1FilePath
        self.csvRefStatsS1FilePath = conf.fCsvRefStatsS1FilePath
        self.binAllStatsS2FilePath = conf.fBinAllStatsS2FilePath
        self.binRefStatsS2FilePath = conf.fBinRefStatsS2FilePath
        self.csvRefStatsS2FilePath = conf.fCsvRefStatsS2FilePath

    def doAllStatsSteps(self):
        a = 3

    def copyShapefiles(self):
        sourceDirectory = Path(self.conf.confArgs.trainingPointsShapefile).parent.absolute()
        fileNameWithoutExt = Path(self.conf.confArgs.trainingPointsShapefile).stem
        src = Path(sourceDirectory)
        filename = fileNameWithoutExt
        dst = Path(self.statsDir)
        shpNameFile = 'trainingShp'
        self.trainingPointsShapefile = Path(dst, shpNameFile + '.shp')
        idx = 0
        for file in src.iterdir():
            if file.is_file() and file.stem == filename:
                idx += 1
                outFile = (dst / shpNameFile).with_suffix(file.suffix)
                copy(file, outFile)
                self.conf.trySaveFileWithS3(outFile)

    def copySegmentationFile(self):
        if not Path(self.workingRasterTrainingPoints).exists() or self.conf.confArgs.overwrite:
            copy(self.segmentationTiffFile, self.workingRasterSegmentation)
            self.conf.trySaveFileWithS3(self.workingRasterSegmentation)

    def drawPoints(self):
        if self.workingRasterTrainingPoints.exists() and self.workingRasterTrainingPoints.stat().st_size > 1024 and not self.conf.confArgs.overwrite:
            return
        dataSrc = gdal.Open(str(self.workingRasterSegmentation))

        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create(
            str(self.workingRasterTrainingPoints),
            dataSrc.RasterXSize,
            dataSrc.RasterYSize,
            1,
            gdal.GDT_UInt32,
            ['COMPRESS=LZW'])
        dst_ds.SetGeoTransform(dataSrc.GetGeoTransform())
        dst_ds.SetProjection(dataSrc.GetProjection())
        i = 0
        for c in self.conf.confArgs.classesToClassify:
            whereCond = '"' + self.conf.confArgs.trainingColumnInShapefile + '"=\'' + self.conf.confArgs.classesToClassify[i] + '\''
            OPTIONS = gdal.RasterizeOptions(burnValues=[i + 1], where=whereCond)
            print('rasterize:' + whereCond)
            gdal.Rasterize(dst_ds, str(self.workingTrainingPointsShapefile), options=OPTIONS)
            i = i + 1
        self.conf.trySaveFileWithS3(self.workingRasterTrainingPoints)

    def runSystemProcess(self, command):
        # if not self.outputCommandsFileHandle.closed:
        #     self.outputCommandsFileHandle.write(command)
        #     self.outputCommandsFileHandle.write('\n')
        print('\n' + command)
        os.system(command)

    def runCoord(self):
        command = self.conf.prepareProgramExePath
        command = command + ' coord ' + str(self.conf.segmentationRasterFile) + ' ' + str(self.binCoordFilePath)
        self.runSystemProcess(command)
        self.conf.trySaveFileWithS3(self.binCoordFilePath)

    def runCoordRef(self):
        command = self.conf.prepareProgramExePath
        command = command + ' coordRef ' + str(self.conf.segmentationRasterFile) + ' ' + str(self.workingRasterTrainingPoints) + ' ' + str(self.binRefCoordFilePath)
        self.runSystemProcess(command)
        self.conf.trySaveFileWithS3(self.binRefCoordFilePath)

    def dirListToStr(self, list):
        strList = ''
        for d in list:
            strList = strList + ' "' + str(d) + '"'
        return strList

    def runLoadMultiTempRefS1(self):
        command = self.conf.prepareProgramExePath
        command = command + ' loadMultiTempRef ' + str(self.binRefCoordFilePath) + ' ' + str(self.csvRefStatsS1FilePath) + ' ' + str(self.binRefStatsS1FilePath)
        dirList = self.conf.getS1TimesDirs()
        command = command + self.dirListToStr(dirList)
        self.runSystemProcess(command)
        self.conf.trySaveFileWithS3(self.binRefStatsS1FilePath)
        self.conf.trySaveFileWithS3(self.csvRefStatsS1FilePath)

    def runLoadMultiTempS1(self):
        command = self.conf.prepareProgramExePath
        command = command + ' loadMultiTemp ' + str(self.binCoordFilePath) + ' ' + str(self.binAllStatsS1FilePath)
        dirList = self.conf.getS1TimesDirs()
        command = command + self.dirListToStr(dirList)
        self.runSystemProcess(command)
        self.conf.trySaveFileWithS3(self.binAllStatsS1FilePath)

    def runLoadMultiTempS2(self):
        command = self.conf.prepareProgramExePath
        command = command + ' loadMultiTempS2 ' + str(self.binCoordFilePath) + ' ' + str(self.binAllStatsS2FilePath)
        dirList = self.conf.getS2TimesDirs()
        command = command + self.dirListToStr(dirList)
        self.runSystemProcess(command)

    def runLoadMultiTempRefS2(self):
        command = self.conf.prepareProgramExePath
        command = command + ' loadMultiTempS2Ref ' + str(self.binRefCoordFilePath) + ' ' + str(self.csvRefStatsS2FilePath) + ' ' + str(self.binRefStatsS2FilePath)
        dirList = self.conf.getS2TimesDirs()
        command = command + self.dirListToStr(dirList)
        self.runSystemProcess(command)
        self.conf.trySaveFileWithS3(self.binRefStatsS1FilePath)
        self.conf.trySaveFileWithS3(self.csvRefStatsS1FilePath)

    def doPrepareSteps(self):
        self.copyShapefiles()
        self.copySegmentationFile()
        self.drawPoints()
        if self.conf.overwrite or not self.binRefCoordFilePath.is_file():
            self.runCoordRef()
        if self.conf.overwrite or not self.binCoordFilePath.is_file():
            self.runCoord()

    def doAllS1Steps(self):
        if Path(self.conf.confArgs.S1DataMainDir).is_dir():
            self.doPrepareSteps()
            if self.conf.RefS1:
                if self.conf.overwrite or not self.binRefStatsS1FilePath.is_file():
                    self.runLoadMultiTempRefS1()
            if self.conf.AllS1:
                if self.conf.overwrite or not self.binAllStatsS1FilePath.is_file():
                    self.runLoadMultiTempS1()

    def doAllS2Steps(self):
        if Path(self.conf.confArgs.S2DataMainDir).is_dir():
            self.doPrepareSteps()
            if self.conf.RefS2:
                if self.conf.overwrite or not self.binRefStatsS2FilePath.is_file():
                    self.runLoadMultiTempRefS2()
            if self.conf.AllS2:
                if self.conf.overwrite or not self.binAllStatsS2FilePath.is_file():
                    self.runLoadMultiTempS2()

    def doAllSteps(self):
        self.doAllS1Steps()
        self.doAllS2Steps()
        # self.copyShapefiles()
        # self.copySegmentationFile()
        # self.drawPoints()
        # if self.conf.overwrite or not self.binRefCoordFilePath.is_file():
        #     self.runCoordRef()
        # if self.conf.overwrite or not self.binCoordFilePath.is_file():
        #     self.runCoord()
        # if self.conf.RefS1:
        #     if self.conf.overwrite or not self.binRefStatsS1FilePath.is_file():
        #         self.runLoadMultiTempRefS1()
        # if self.conf.AllS1:
        #     if self.conf.overwrite or not self.binAllStatsS1FilePath.is_file():
        #         self.runLoadMultiTempS1()
        # if self.conf.RefS2:
        #     if self.conf.overwrite or not self.binRefStatsS2FilePath.is_file():
        #         self.runLoadMultiTempRefS2()
        # if self.conf.AllS2:
        #     if self.conf.overwrite or not self.binAllStatsS2FilePath.is_file():
        #         self.runLoadMultiTempS2()
