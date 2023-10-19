import cv2
import torch
import torch.nn as nn
import torch.nn.functional as f
import torch.optim as optim
from test.StatusDescriptor.conftest import getSampleInventorySlicerNotInTest
from src.StatusDescriptor.sliceReader import InventorySliceReader


class DigitSliceRecognizer(nn.Module):
    def __init__(self, sliceSize, savedModelPath=""):
        super().__init__()
        self.__configNet(sliceSize)
        self.__configTraining()
        self.__loadSavedModel(savedModelPath)

    def forward(self, x):
        x = cv2.resize(x, (self.width, self.height))
        x = InventorySliceReader.convertImageToMonoChrome(x)
        x = torch.from_numpy(x)
        x = x.view(-1)
        x = x.float()
        x = self.fc(x)
        x = f.relu(x)
        return x

    def __configNet(self, sliceSize):
        self.width = sliceSize['width']
        self.height = sliceSize['height']
        self.inputPixels = self.width * self.height
        numDigitTypes = 10
        self.fc = nn.Linear(self.inputPixels, numDigitTypes)

    def __configTraining(self):
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.SGD(self.parameters(), lr=0.001, momentum=0.9)
        self.epochs = 5

    def __loadSavedModel(self, savedModelPath):
        if savedModelPath != "":
            self.load_state_dict(torch.load(savedModelPath))
            self.eval()

    def trainNet(self, sliceWithLabels):
        print("start training")
        for epoch in range(self.epochs):
            for _slice, label in sliceWithLabels:
                inputs = _slice.getImage()
                self.optimizer.zero_grad()
                outputs = self(inputs)
                loss = self.criterion(outputs, label)
                loss.backward()
                self.optimizer.step()
            print(f"[{epoch + 1}] loss: {loss.item()}")
        print("finished training")


def prepare_slice_with_labels():
    sliceWithLabels = []
    for i in range(10):
        slices = getSampleInventorySlicerNotInTest(i).getSlices()
        label = [1.0 if i == j else 0.0 for j in range(10)]
        label = torch.tensor(label)
        labeledSlices = [(s, label) for s in slices]
        sliceWithLabels.extend(labeledSlices)
    return sliceWithLabels


def train_and_save_DigitSliceRecognizer():
    sliceWithLabels = prepare_slice_with_labels()
    aSlice, _ = sliceWithLabels[0]
    recognizer = DigitSliceRecognizer(aSlice.getSize())
    recognizer.trainNet(sliceWithLabels)
    torch.save(recognizer.state_dict(), "digitSliceRecognizer.pth")


if __name__ == "__main__":
    train_and_save_DigitSliceRecognizer()
