import os
from pathlib import Path
from shutil import copy
from osgeo import gdal
from osgeo import ogr
from Configuration import Configuration

class StatsCreator:
    def __init__(self, conf: Configuration):
        self.outputCommandsFilePath = ''
        self.outputCommandsFileHandle = 0
        self.conf = conf
        self.statsDir = conf.statsDir
        self.trainingPointsShapefile = conf.trainingPointsShapefile
        self.segmentationTiffFile = conf.segmentationTiffFile
        self.workingTrainingPointsShapefile = Path(self.statsDir, 'trainingShp.shp')
        self.workingRasterTrainingPoints = Path(self.statsDir, 'segmentsPointsSelected.tif')
        self.outputCommandsFilePath = Path(self.conf.workingDir, 'commands.txt')
        self.outputCommandsFileHandle = open(self.outputCommandsFilePath, "w")
        self.binCoordFilePath = Path(self.statsDir, 'allCoords.bin')
        self.binRefCoordFilePath = Path(self.statsDir, 'RefCoordsSelected.bin')
        self.binAllStatsS1FilePath = Path(self.statsDir, 'allStatsS1.bin')
        self.binRefStatsS1FilePath = Path(self.statsDir, 'refStatsS1.bin')
        self.csvRefStatsS1FilePath = Path(self.statsDir, 'refStatsS1.csv')
        self.binAllStatsS2FilePath = Path(self.statsDir, 'allStatsS2.bin')
        self.binRefStatsS2FilePath = Path(self.statsDir, 'refStatsS2.bin')
        self.csvRefStatsS2FilePath = Path(self.statsDir, 'refStatsS2.csv')

    def copyShapefiles(self):
        sourceDirectory = Path(self.trainingPointsShapefile).parent.absolute()
        fileNameWithoutExt = Path(self.trainingPointsShapefile).stem
        src = Path(sourceDirectory)
        filename = fileNameWithoutExt
        dst = Path(self.statsDir)
        idx = 0
        for file in src.iterdir():
            if file.is_file() and file.stem == filename:
                idx += 1
                copy(file, (dst / f"trainingShp").with_suffix(file.suffix))

    def copySegmentationFile(self):
        destFile = Path(self.statsDir, 'segmentsPolygons.tif')
        destPointsFile = self.workingRasterTrainingPoints
        copy(self.segmentationTiffFile, destFile)
        # copy(self.segmentationTiffFile, destPointsFile)

    def drawPoints(self):
        dataSrc = gdal.Open(self.segmentationTiffFile)
        shp = ogr.Open(str(self.workingTrainingPointsShapefile))
        lyr = shp.GetLayer()
        feature = lyr.GetNextFeature()

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
        for c in self.conf.classesList:
            whereCond = '"' + self.conf.trainingClassesColumnName + '"=\'' + self.conf.classesList[i] + '\''
            OPTIONS = gdal.RasterizeOptions(burnValues=[i+1], where=whereCond)
            print('rasterize:' + whereCond)
            gdal.Rasterize(dst_ds, str(self.workingTrainingPointsShapefile), options=OPTIONS)
            i = i+1

    def runSystemProcess(self, command):
        if not self.outputCommandsFileHandle.closed:
            self.outputCommandsFileHandle.write(command)
            self.outputCommandsFileHandle.write('\n')
        print('\n' + command)
        os.system(command)

    def runCoord(self):
        command = self.conf.prepareProgramExePath
        command = command + ' coord ' + str(self.conf.segmentationTiffFile) + ' ' + str(self.binCoordFilePath)
        self.runSystemProcess(command)

    def runCoordRef(self):
        command = self.conf.prepareProgramExePath
        command = command + ' coordRef ' + str(self.conf.segmentationTiffFile) + ' ' + str(self.workingRasterTrainingPoints) + ' ' + str(self.binRefCoordFilePath)
        self.runSystemProcess(command)

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

    def runLoadMultiTempS1(self):
        command = self.conf.prepareProgramExePath
        command = command + ' loadMultiTemp ' + str(self.binCoordFilePath) + ' ' + str(self.binAllStatsS1FilePath)
        dirList = self.conf.getS1TimesDirs()
        command = command + self.dirListToStr(dirList)
        self.runSystemProcess(command)

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

    def doAllS1Steps(self):
        self.copyShapefiles()
        self.copySegmentationFile()
        self.drawPoints()
        if self.conf.overwrite or not self.binRefCoordFilePath.is_file():
            self.runCoordRef()
        if self.conf.overwrite or not self.binCoordFilePath.is_file():
            self.runCoord()
        if self.conf.RefS1:
            if self.conf.overwrite or not self.binRefStatsS1FilePath.is_file():
                self.runLoadMultiTempRefS1()
        if self.conf.AllS1:
            if self.conf.overwrite or not self.binAllStatsS1FilePath.is_file():
                self.runLoadMultiTempS1()

    def doAllS2Steps(self):
        self.copyShapefiles()
        self.copySegmentationFile()
        self.drawPoints()
        if self.conf.overwrite or not self.binRefCoordFilePath.is_file():
            self.runCoordRef()
        if self.conf.overwrite or not self.binCoordFilePath.is_file():
            self.runCoord()
        if self.conf.RefS2:
            if self.conf.overwrite or not self.binRefStatsS2FilePath.is_file():
                self.runLoadMultiTempRefS2()
        if self.conf.AllS2:
            if self.conf.overwrite or not self.binAllStatsS2FilePath.is_file():
                self.runLoadMultiTempS2()

    def doAllSteps(self):
        self.copyShapefiles()
        self.copySegmentationFile()
        self.drawPoints()
        if self.conf.overwrite or not self.binRefCoordFilePath.is_file():
            self.runCoordRef()
        if self.conf.overwrite or not self.binCoordFilePath.is_file():
            self.runCoord()
        if self.conf.RefS1:
            if self.conf.overwrite or not self.binRefStatsS1FilePath.is_file():
                self.runLoadMultiTempRefS1()
        if self.conf.AllS1:
            if self.conf.overwrite or not self.binAllStatsS1FilePath.is_file():
                self.runLoadMultiTempS1()
        if self.conf.RefS2:
            if self.conf.overwrite or not self.binRefStatsS2FilePath.is_file():
                self.runLoadMultiTempRefS2()
        if self.conf.AllS2:
            if self.conf.overwrite or not self.binAllStatsS2FilePath.is_file():
                self.runLoadMultiTempS2()
