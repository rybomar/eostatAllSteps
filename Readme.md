Simplified launch of classification and collection of statistics (S-1 and S-2) in EOSTAT project.  

###Input data  
- Data from satellite images:
  - Sentinel-1 data processed with MT_SAR and cataloged in directories with MMDD names,   
  or
  - Sentinel-2 data processed with...[TBD],
- Raster file with segmentation of interested area,
- Shapefile with all interested classes saved as points (one point per parcel),
- list of classes to classify  

###Requirements/dependiences
Before running the program, be sure that you have installed Python 3 with libraries:  
joblib, numpy, sklearn, pathlib, json, shutil, osgeo (gdal, ogr), openpyxl  

###Launching
1. Prepare configuration file, e.g. `configurationFile.json`
2. run:  
`python main.py configurationFile.json`
   
###Preparing configuration file
The easiest way to prepare the file is to open an example: `configurationArgsFilled.json` and edit some lines.  
The meaning of each parameter in this file:  
- **"S1DataMainDir"** - a directory with S-1 data, usually with division for orbits (P1, P2, etc.), 
- **"S2DataMainDir"** - a directory with S-2 data, usually with division for orbits (P1, P2, etc.),
- **"classesToClassify"** - list of classes (from vector file) to classify,
- **"optionStratificationCounts"** - list of numbers for random selection for each class; if not set all points will be used ,
- **"options"**: - list of type of input for classification; if S1-based classification, type: ["AllS1", "RefS1"]; if S1+S2-based classification, type: ["AllS1", "RefS1", "AllS2", "RefS2"]
- **"orbitNumber"**: - if Poland, type a number from 1 to 6, otherwise 0 or ask a question
- **"overwrite"**: - true or false,
- **"segmentationRasterFile**: - file with segmentation (e.g. from ecognition),
- **"trainingColumnInShapefile"**: - column from attribute table with names of classes,
- **"trainingPointsShapefile"** - a path to shapefile with reference data,
- **"workingDir"** - path to directory to store temporary data and results,
- **"optionClassifierMaxDepth"** - random forest option,
- **"optionClassifierNEstimators"** - random forest option,
- **"optionNJobs"** - random forest option (number of threads)

