from . import validators
from ruamel.yaml import YAML


class Slice:
    def __init__(self, _id, _type, referencePoint, size):
        self._id = _id
        self._type = _type
        self._referencePoint = referencePoint
        self._size = size

        self._pixel = None
        self._value = None

    def isSliced(self):
        return self._pixel is not None

    def isProcessed(self):
        return self._value is not None

    def getId(self):
        return self._id

    def getType(self):
        return self._type

    def getReferencePoint(self):
        return self._referencePoint

    def getSize(self):
        return self._size

    def getImage(self):
        if not self.isSliced():
            raise ValueError("before getting pixel, you must slice the image")
        return self._pixel

    def getValue(self):
        if not self.isProcessed():
            raise ValueError("before getting value, you must process the slice")
        return self._value

    def setPixel(self, pixel):
        self._pixel = pixel

    def setValue(self, value):
        self._value = value


class ImageSlicer:
    def __init__(self, image):
        self._isColoredImage(image)
        self._image = image
        self._width, self._height, _ = image.shape

    def _fillImageToSlice(self, sliceIn):
        referencePoint = sliceIn.getReferencePoint()
        size = sliceIn.getSize()

        x = referencePoint['x']
        y = referencePoint['y']
        width = size['width']
        height = size['height']

        sliceIn.setPixel(self._image[y:y + height, x:x + width])
        return sliceIn

    @staticmethod
    def _isColoredImage(image):
        return validators.colored_image_validator(image)

    @staticmethod
    def _isCrafterWindow(image):
        return validators.crafter_window_validator(image)


class InventorySlicer(ImageSlicer):
    def __init__(self, image, config):
        super()._isCrafterWindow(image)
        super().__init__(image)
        self._slices = self.__getSlicesFromConfig(config)
        self.image = image

    def __getSlicesFromConfig(self, c):
        rawConfig = c["items"]
        commonSize = c["commonSize"]
        configWithSize = InventorySlicer.__expandConfigWithCommonSize(rawConfig, commonSize)

        slices = []
        for k, v in configWithSize.items():
            s = Slice(k, "inventory", v["referencePoint"], v["size"])
            super()._fillImageToSlice(s)
            slices.append(s)
        return slices

    @staticmethod
    def __expandConfigWithCommonSize(d, commonSize):
        for k, v in d.items():
            if v["isCommonSize"]:
                d[k]["size"] = commonSize
        return d

    def getItemNames(self):
        names = []
        for s in self._slices:
            names.append(s.getId())
        return names

    def getSlices(self):
        return self._slices


class SurroundingSlicer(ImageSlicer):
    def __init__(self, image, config):
        super()._isCrafterWindow(image)
        super().__init__(image)
        self._slices = self.__getSlicesFromConfig(config)

    def __getSlicesFromConfig(self, c):
        gridIds = SurroundingSlicer.__getGridSliceCoordinatesFromConfig(c)
        gridSizeInPixel = c["grid"]["sizeInPixel"]

        slices = []
        for _id in gridIds:
            referencePoint = SurroundingSlicer.__gridReferencePoint(_id, c)
            s = Slice(_id, "surrounding", referencePoint, gridSizeInPixel)
            super()._fillImageToSlice(s)
            slices.append(s)
        return slices

    @staticmethod
    def __getGridSliceCoordinatesFromConfig(config):
        playerOffsetInGridCounts = config["offsets"]["playerInGridCounts"]
        totalGridCounts = config["grid"]["totalCounts"]

        gridCoordinates = []
        for x in range(totalGridCounts["width"]):
            for y in range(totalGridCounts["height"]):
                gridCoordinates.append({"x": x - playerOffsetInGridCounts["x"],
                                        "y": y - playerOffsetInGridCounts["y"]})
        return gridCoordinates

    @staticmethod
    def __gridReferencePoint(gridId, config):
        offsets = config["offsets"]
        windowOffsetInPixel = offsets["windowInPixel"]
        playerOffsetInGridCounts = offsets["playerInGridCounts"]
        gridSizeInPixel = config["grid"]["sizeInPixel"]

        referencePointX = (gridSizeInPixel["width"] * (gridId["x"] + playerOffsetInGridCounts["x"])
                           + windowOffsetInPixel["x"])
        referencePointY = (gridSizeInPixel["height"] * (gridId["y"] + playerOffsetInGridCounts["y"])
                           + windowOffsetInPixel["y"])
        return {"x": referencePointX, "y": referencePointY}

    def getSlices(self):
        return self._slices


class PlayWindowSlicer:
    def __init__(self, image, configFilePath="config.yaml"):
        config = PlayWindowSlicer.__loadConfigFile(configFilePath)
        inventoryConfig = PlayWindowSlicer.__getInventoryConfigFromWholeConfig(config)
        surroundingConfig = PlayWindowSlicer.__getSurroundingConfigFromWholeConfig(config)
        self.inventorySlicer = InventorySlicer(image, inventoryConfig)
        self.surroundingSlicer = SurroundingSlicer(image, surroundingConfig)

    def getSlices(self):
        return [self.inventorySlicer.getSlices(), self.surroundingSlicer.getSlices()]

    def getInventoryItemNames(self):
        return self.inventorySlicer.getItemNames()

    @staticmethod
    def __loadConfigFile(configFilePath):
        yaml = YAML()
        with open(configFilePath, "r") as f:
            config = yaml.load(f)
        return config

    @staticmethod
    def __getInventoryConfigFromWholeConfig(config):
        return config["PlayWindowSlicer"]["inventory"]

    @staticmethod
    def __getSurroundingConfigFromWholeConfig(config):
        return config["PlayWindowSlicer"]["surrounding"]
