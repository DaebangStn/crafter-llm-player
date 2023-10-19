from ruamel.yaml import YAML
import numpy as np
import pytesseract
import cv2


class InventorySliceReader:
    def __init__(self, config):
        self.__setConfig(config)

    def read(self, _slice):
        if _slice.isProcessed():
            return
        image = self.convertImageToMonoChrome(_slice.getImage())
        _slice.setValue(self.__processOcr(image))

    def __setConfig(self, c):
        self.scanThreshold = c["scanThreshold"]
        self.emptyThreshold = c["emptyThreshold"]

    @staticmethod
    def convertImageToMonoChrome(image):
        maxPixelValue = 255
        scanThreshold = 254
        grayImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        _, monoChromeImage = cv2.threshold(grayImage, scanThreshold, maxPixelValue, cv2.THRESH_BINARY)
        return monoChromeImage

    def __processOcr(self, image):
        ocrOut = pytesseract.image_to_string(
            image, config='--psm 7 -c tessedit_char_whitelist=123456789 -c user-patterns=\\\[1-9]{1}')
        if len(ocrOut) > 0:
            ocrValue = 0
            try:
                ocrValue = int(ocrOut[0])
            except ValueError:
                pass
            finally:
                print(f"ocrOut: {ocrOut}, ocrValue: {ocrValue}")
                return ocrValue

        print("ocrOut is empty")
        if np.mean(image) > self.emptyThreshold:
            return 4
        else:
            return 0


class SurroundingSliceReader:
    def read(self, _slice):
        if _slice.isProcessed():
            return


class SliceReader:
    def __init__(self, configFilePath="configs.yaml"):
        config = SliceReader.__loadConfigFile(configFilePath)
        inventoryConfig = SliceReader.__getInventoryConfigFromWholeConfig(config)
        self.surroundingReader = SurroundingSliceReader()
        self.inventoryReader = InventorySliceReader(inventoryConfig)

    def read(self, _slices):
        for _slice in _slices:
            if _slice.getType() == "surrounding":
                self.surroundingReader.read(_slice)
            if _slice.getType() == "inventory":
                self.inventoryReader.read(_slice)
        return _slices

    @staticmethod
    def __loadConfigFile(configFilePath):
        yaml = YAML()
        with open(configFilePath, "r") as f:
            config = yaml.load(f)
        return config

    @staticmethod
    def __getInventoryConfigFromWholeConfig(config):
        return config["SliceReader"]["inventory"]
