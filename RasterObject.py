class RasterObject:
    """Stores objects received from raster (segmentation's image) as set of coordinates  and other info."""
    Xs = []
    Ys = []
    id = -1001
    intClass = -1
    features = []
    className = ''

    def __init__(self):
        self.id = -1001
        self.intClass = -1

    def __init__(self, initList):

        first = True
        for value in initList:
            if first:
                self.assignId(value)
                first = False
            else:
                self.addOneCoord(value)

    """Alternately Xs and Ys coordinates."""
    def addOneCoord(self, coordXorY):
        if len(self.Xs) == len(self.Ys):
            self.Xs.append(coordXorY)#add x
        else:
            self.Ys.append(coordXorY)#add y

    def assignId(self, id):
        self.id = id

    def assignClass(self, intclass):
        if intclass < 0:
            intclass = -intclass
        self.intClass = intclass

    def fillFeatures(self, featuresList):
        self.features = featuresList
