import os
import random
import cv2
import numpy as np
import pytest
from src.StatusDescriptor.playWindowSlicer import *
from src.StatusDescriptor.sliceReader import *


@pytest.fixture
def dummySliceWithoutSliced():
    return Slice(0, 'inventory', {'x': 0, 'y': 0}, {'width': 0, 'height': 0})


@pytest.fixture
def dummySliceWithoutProcessed():
    dummySlice = Slice(0, 'inventory', {'x': 0, 'y': 0}, {'width': 0, 'height': 0})
    dummySlice.setPixel(np.array([0, 0, 0]))
    return dummySlice


@pytest.fixture
def dummyBlackImage():
    return np.zeros((1000, 1000, 1), dtype=np.uint8)


@pytest.fixture
def dummyColorImage():
    return np.zeros((1000, 1000, 3), dtype=np.uint8)


@pytest.fixture
def dummyCrafterImage():
    return np.zeros((600, 600, 3), dtype=np.uint8)


def getInventorySampleImagePath(inventoryValue):
    relativeImagePath = f"testCaptureForDescriptor/inventory/inventoryValue-{inventoryValue}.png"
    return getAbsPath(relativeImagePath)


def getFilePathFromSeed(seed, directoryAbsPath):
    filenames = []
    for fn in os.listdir(directoryAbsPath):
        if os.path.isfile(os.path.join(directoryAbsPath, fn)) and fn.endswith(".png"):
            filenames.append(fn)
    if len(filenames) == 0:
        raise FileNotFoundError(f"no png file found in {directoryAbsPath}")
    if seed == -1:
        filename = random.choice(filenames)
        return os.path.join(directoryAbsPath, filename)

    fileWithSeed = [fn for fn in filenames if fn.endswith(f"Seed-{seed}.png")]
    if len(fileWithSeed) == 0:
        raise FileNotFoundError(f"no file with seed {seed} found in {directoryAbsPath}")
    return os.path.join(directoryAbsPath, fileWithSeed[0])


def getTerrainSampleImagePath(seed=-1):
    return getFilePathFromSeed(seed, getAbsPath(f"testCaptureForDescriptor/terrain"))


def getAbsPath(relativePath):
    currentDirAbsPath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(currentDirAbsPath, relativePath)


def getTestConfig(configFileName="configs.yaml"):
    configAbsPath = getAbsPath(configFileName)
    yaml = YAML()
    with open(configAbsPath, "r") as f:
        config = yaml.load(f)
    return config


def getInventorySlicerConfig():
    config = getTestConfig()
    return config["PlayWindowSlicer"]["inventory"]


def getSurroundingSlicerConfig(configFileName="configs.yaml"):
    config = getTestConfig(configFileName)
    return config["PlayWindowSlicer"]["surrounding"]


@pytest.fixture
def getSampleInventorySlicer(getInventoryValue):
    imagePath = getInventorySampleImagePath(getInventoryValue)
    image = cv2.imread(imagePath, cv2.IMREAD_COLOR)
    config = getInventorySlicerConfig()
    return InventorySlicer(image, config)


def getSampleInventorySlicerNotInTest(getInventoryValue):
    imagePath = getInventorySampleImagePath(getInventoryValue)
    image = cv2.imread(imagePath, cv2.IMREAD_COLOR)
    config = getInventorySlicerConfig()
    return InventorySlicer(image, config)


@pytest.fixture(params=[-1])
def getSampleSurroundingSlicerWithTerrainImage(request):
    seed = -1 if request is None else request.param
    imagePath = getTerrainSampleImagePath(seed)
    image = cv2.imread(imagePath, cv2.IMREAD_COLOR)
    config = getSurroundingSlicerConfig("configForTerrain.yaml")
    return SurroundingSlicer(image, config)


@pytest.fixture(params=range(10))
def getInventoryValue(request):
    return request.param


@pytest.fixture
def getSamplePlayWindowSlicerWithInventoryImage(getInventoryValue):
    imagePath = getInventorySampleImagePath(getInventoryValue)
    image = cv2.imread(imagePath, cv2.IMREAD_COLOR)
    return PlayWindowSlicer(image, getAbsPath("configs.yaml"))


@pytest.fixture
def getSliceReader():
    return SliceReader(getAbsPath("configs.yaml"))
