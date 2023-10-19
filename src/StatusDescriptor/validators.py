import numpy as np


def crafter_window_validator(image):
    CRAFTER_IMAGE_SIZE: int = 600

    colored_image_validator(image)
    height, width, _ = image.shape

    if not width == CRAFTER_IMAGE_SIZE and height == CRAFTER_IMAGE_SIZE:
        raise ValueError("crafter window must be 600x600")


def colored_image_validator(image):
    NUM_RGB_CHANNEL: int = 3

    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a numpy array")

    _, _, NUM_IMAGE_CHANNEL = image.shape
    if not NUM_IMAGE_CHANNEL == NUM_RGB_CHANNEL:
        raise ValueError("image must have 3 channels (RGB)")
