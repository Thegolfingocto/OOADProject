import numpy as np
import matplotlib.pyplot as plt
import os

from Parser import *

vecLangs = ["Java", "C++", "Rust"]

def PlotComplexHeightVsLength(N: int = 100) -> None:
    nData = np.zeros((N, len(vecLangs), 2))

    for strLang in vecLangs:
        for n in range(N):
            dData = GetParseData(strLang, n)

            print(dData["ComplexHeight"])


def main():
    PlotComplexHeightVsLength()


if __name__ == "__main__":
    main()