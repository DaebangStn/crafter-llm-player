import pytest
import numpy as np
from src.StatusDescriptor.playWindowSlicer import *


class TestSlice:
    def test_isSliced(self, dummySliceWithoutSliced, dummySliceWithoutProcessed):
        assert not dummySliceWithoutSliced.isSliced()
        assert dummySliceWithoutProcessed.isSliced()


class TestImageSlicer:
    def test_initializer(self, dummyBlackImage, dummyColorImage):
        with pytest.raises(TypeError):
            ImageSlicer(0)
        with pytest.raises(ValueError):
            ImageSlicer(dummyBlackImage)
        ImageSlicer(dummyColorImage)


class TestInventorySlicer:
    def test_initializer(self, getSampleInventorySlicer):
        getSampleInventorySlicer.getItemNames()
        getSampleInventorySlicer.getSlices()


class TestSurroundingSlicer:
    def test_initializer(self, getSampleSurroundingSlicerWithTerrainImage):
        getSampleSurroundingSlicerWithTerrainImage.getSlices()


class TestPlayWindowSlicer:
    def test_initializer(self, getSamplePlayWindowSlicerWithInventoryImage):
        getSamplePlayWindowSlicerWithInventoryImage.getInventoryItemNames()
        getSamplePlayWindowSlicerWithInventoryImage.getSlices()
