import cv2
import pytest


class TestSliceReader:
    def test_initializer(self, getSliceReader):
        getSliceReader.read([])


class TestInventorySliceReader:
    def test_read(self, getInventoryValue, getSampleInventorySlicer, getSliceReader):
        slices = getSampleInventorySlicer.getSlices()
        slices = getSliceReader.read(slices)
        for s in slices:
            assert s.isProcessed()
            assert TestInventorySliceReader.readIsCorrect(s, getInventoryValue, getSliceReader.inventoryReader), \
                f"For {s.getId()} Slice, expected {getInventoryValue}, but got {s.getValue()}"

    @staticmethod
    def readIsCorrect(_slice, expectedValue, inventoryReader):
        exceptionalCondition = _slice.getId() == "health" and expectedValue == 0
        normalCase = _slice.getValue() == expectedValue and not exceptionalCondition
        exceptionCase = _slice.getValue() == 1 and exceptionalCondition
        isCorrect = normalCase or exceptionCase

        if not isCorrect:
            monoChromeImage = inventoryReader.convertImageToMonoChrome(_slice.getImage())
            cv2.imshow(f"expected {expectedValue}", monoChromeImage)
            cv2.waitKey(0)

        return isCorrect


class TestSurroundingSliceReader:
    def test_read(self, getSampleSurroundingSlicerWithTerrainImage, getSliceReader):
        slices = getSampleSurroundingSlicerWithTerrainImage.getSlices()
        getSliceReader.read(slices)
