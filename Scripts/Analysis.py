import numpy as np
import matplotlib.pyplot as plt
import tqdm

from Parser import *

vecLangs = ["Java", "C++", "Rust"]

def PlotComplexHeightVsLength(N: int = 10000) -> None:
    vecData = [np.zeros((N, 2)) for _ in range(len(vecLangs))]

    for l in range(len(vecLangs)):
        strLang = vecLangs[l]
        for n in tqdm.tqdm(range(N)):
            dData = GetParseData(strLang, n)

            vecData[l][n, 0] = len(dData["Funcs"])
            vecData[l][n, 1] = dData["ComplexHeight"]
    


    for l in range(len(vecLangs)):
        strLang = vecLangs[l]

        fIdx = np.where(vecData[l][:, 0] > 5)
        print(fIdx[0].shape[0])
        print(fIdx[0].shape[0] / 10000)
        vecData[l] = vecData[l][fIdx]

        print(np.min(vecData[l][:, 0]), np.max(vecData[l][:, 0]))

        X = np.sort(np.unique(vecData[l][:, 0]))
        Y = []
        for i in range(X.shape[0]):
            x = X[i]
            sIdx = np.where(vecData[l][:, 0] == x)
            Y.append(np.median(vecData[l][sIdx[0], 1]))

        plt.plot(X, Y, label = strLang, linewidth = 3)

    plt.legend(fontsize = 26)
    plt.show()
    plt.close()

def main():
    PlotComplexHeightVsLength()


if __name__ == "__main__":
    main()