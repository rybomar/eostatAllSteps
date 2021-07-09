from Configuration import Configuration
from osgeo import gdal
from pathlib import Path
import numpy as np
from shutil import copyfile
import os
from ClassificationProcess import ClassificationProcess


class MergeCreator:
    def __init__(self, config: Configuration):
        self.config = config
        self.classificationRasterPaths = []
        self.probabilityRasterPaths = []
        self.emptyMergePath = ''
        self.tempClassificationWithEmptyRasterPaths = []
        self.tempProbabilityWithEmptyRasterPaths = []
        Ps = [1, 2, 3, 4, 5, 6]
        for p in Ps:
            self.config.confArgs.orbitNumber = p
            foundClassificationTif = ''
            foundProbabilityTif = ''
            classprocess = ClassificationProcess(self.config)
            classprocess.saveClassificationToRaster(self.config)  # try to convert results to to tif (sometimes it isn't done)
            clRasterPath = Path(self.config.confArgs.workingDir, 'P' + str(p), 'stats', 'resultClasses.tif')
            if clRasterPath.exists():
                foundClassificationTif = clRasterPath
            prRasterPath = Path(self.config.confArgs.workingDir, 'P' + str(p), 'stats', 'resultProbability.tif')
            prRasterPath256 = Path(self.config.confArgs.workingDir, 'P' + str(p), 'stats', 'probability256.tif')
            if prRasterPath.exists():
                foundProbabilityTif = prRasterPath
            elif prRasterPath256.exists():
                foundProbabilityTif = prRasterPath256
            if len(str(foundClassificationTif)) > 0 and len(str(foundProbabilityTif)) > 0:
                self.classificationRasterPaths.append(foundClassificationTif)
                self.probabilityRasterPaths.append(foundProbabilityTif)
            else:
                infoStr = 'No valid result in P' + str(p) + ' folder. Skipping it.'
                print(infoStr)

    def createEmptyMerge(self):
        self.emptyMergePath = Path(self.config.confArgs.workingDir, 'emptyMerge.tif')
        gdal_warp_options = gdal.WarpOptions(dstSRS='EPSG:32634', srcNodata=0, dstNodata=0, multithread=True,
                                             warpOptions="NUM_THREADS=ALL_CPUS", creationOptions=["COMPRESS=LZW", "BIGTIFF=YES"])
        image_to_mosaic: list = list()
        for f in self.classificationRasterPaths:
            image_to_mosaic.append(str(f))
        gdal.Warp(destNameOrDestDS=str(self.emptyMergePath),
                  srcDSOrSrcDSTab=image_to_mosaic,
                  options=gdal_warp_options)
        img = gdal.Open(str(self.emptyMergePath), gdal.GA_Update)
        output_array = np.array(img.GetRasterBand(1).ReadAsArray(), dtype=np.uint8)
        output_array[output_array != 0] = 0
        img.GetRasterBand(1).WriteArray(output_array)

    def createMergeWithEmptyEachOne(self):
        for n in range(len(self.classificationRasterPaths)):
            gdal_warp_options = gdal.WarpOptions(dstSRS='EPSG:32634', srcNodata=0, dstNodata=0, multithread=True,
                                                 warpOptions="NUM_THREADS=ALL_CPUS", creationOptions=["COMPRESS=LZW", "BIGTIFF=YES"])
            tempClassificationWithEmptyRasterPath = Path(self.config.confArgs.workingDir, 'tempResultClasses' + str(n) + '.tif')
            self.tempClassificationWithEmptyRasterPaths.append(tempClassificationWithEmptyRasterPath)
            image_to_mosaic: list = list()
            image_to_mosaic.append(str(self.emptyMergePath))
            image_to_mosaic.append(str(self.classificationRasterPaths[n]))
            if not tempClassificationWithEmptyRasterPath.exists():
                gdal.Warp(destNameOrDestDS=str(tempClassificationWithEmptyRasterPath),
                          srcDSOrSrcDSTab=image_to_mosaic,
                          options=gdal_warp_options)
            tempProbabilityWithEmptyRasterPath = Path(self.config.confArgs.workingDir, 'tempResultProbability' + str(n) + '.tif')
            self.tempProbabilityWithEmptyRasterPaths.append(tempProbabilityWithEmptyRasterPath)
            image_to_mosaic: list = list()
            image_to_mosaic.append(str(self.emptyMergePath))
            image_to_mosaic.append(str(self.probabilityRasterPaths[n]))
            if not tempProbabilityWithEmptyRasterPath.exists():
                gdal.Warp(destNameOrDestDS=str(tempProbabilityWithEmptyRasterPath),
                          srcDSOrSrcDSTab=image_to_mosaic,
                          options=gdal_warp_options)

    def calcMergeOnOverlaps(self):
        N = len(self.classificationRasterPaths)
        Y = X = 0
        probNmatrix = []
        classNmatrix = []

        for n in range(N):
            prob = gdal.Open(str(self.tempProbabilityWithEmptyRasterPaths[n]), gdal.GA_ReadOnly)
            probData = np.array(prob.GetRasterBand(1).ReadAsArray(), dtype=np.uint8)
            if n == 0:
                Y, X = probData.shape
                probNmatrix = np.zeros([Y, X, N], dtype=np.uint8)
            probNmatrix[:, :, n] = probData

        maxInd2 = np.argmax(probNmatrix, axis=2)  # which band (belt) has the hisghest value of probability
        I, J = np.ogrid[:Y, :X]
        winProbMatrix = probNmatrix[I, J, maxInd2]
        probNmatrix = None

        for n in range(N):
            clas = gdal.Open(str(self.tempClassificationWithEmptyRasterPaths[n]), gdal.GA_ReadOnly)
            clasData = np.array(clas.GetRasterBand(1).ReadAsArray(), dtype=np.uint8)
            if n == 0:
                Y, X = clasData.shape
                classNmatrix = np.zeros([Y, X, N], dtype=np.uint8)
            classNmatrix[:, :, n] = clasData

        winClassMatrix = classNmatrix[I, J, maxInd2]
        classNmatrix = None

        classFinalPath = Path(self.config.confArgs.workingDir, 'ResultFinal.tif')
        probaFinalPath = Path(self.config.confArgs.workingDir, 'ProbabilityFinal.tif')
        copyfile(self.emptyMergePath, classFinalPath)
        copyfile(self.emptyMergePath, probaFinalPath)

        classFinal = gdal.Open(str(classFinalPath), gdal.GA_Update)
        classFinal.GetRasterBand(1).WriteArray(winClassMatrix)
        print('Final result after merge saved in: ' + str(classFinalPath))

        probabFinal = gdal.Open(str(probaFinalPath), gdal.GA_Update)
        probabFinal.GetRasterBand(1).WriteArray(winProbMatrix)

    def deleteTempFiles(self):
        for f in self.tempClassificationWithEmptyRasterPaths:
            os.remove(f)
        for f in self.tempProbabilityWithEmptyRasterPaths:
            os.remove(f)
        os.remove(self.emptyMergePath)

    def createMerge(self):
        self.createEmptyMerge()
        self.createMergeWithEmptyEachOne()
        self.calcMergeOnOverlaps()
        self.deleteTempFiles()
