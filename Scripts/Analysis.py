import numpy as np
import matplotlib.pyplot as plt
import tqdm

from Parser import *

vecLangs = ["Java", "C++", "Rust"]
vecLangColors = ["lime", "cyan", "orangered"]

def PlotComplexScalars(N: int = 10000, idxY: int = 1, bPlotStd: bool = False, bHDists: bool = False) -> None:
    '''
    Channel list:
    0 -> Number of Functions
    1 -> Complex Height 
    2 -> Number of SubFunctions
    3 -> Number of low rank functions
    4 -> Number of high rank functions
    '''


    #----------------Data loading and pre-proc-----------------#
    iRankSplit = 3

    vecData = [np.zeros((N, 5)) for _ in range(len(vecLangs))]

    vecFullData = [[] for _ in range(len(vecLangs))]

    for l in range(len(vecLangs)):
        strLang = vecLangs[l]
        for n in tqdm.tqdm(range(N)):
            dData = GetParseData(strLang, n)
            if len(dData["Funcs"]) > 5 and dData["ComplexHeight"] < 15:
                vecFullData[l].append(dData)

            vecData[l][n, 0] = len(dData["Funcs"])
            vecData[l][n, 1] = dData["ComplexHeight"]
            vecData[l][n, 2] = len(dData["SubFuncs"])

            NumRanks = np.array(dData["NumCellsPerRank"])
            if NumRanks.shape[0] < iRankSplit:
                vecData[l][n, 3] = np.sum(NumRanks)
            else:
                vecData[l][n, 3] = np.sum(NumRanks[:iRankSplit])
                vecData[l][n, 4] = np.sum(NumRanks[iRankSplit:])

        fIdx = np.where(vecData[l][:, 0] > 5)
        print(fIdx[0].shape[0])
        print(fIdx[0].shape[0] / 10000)
        vecData[l] = vecData[l][fIdx]

        fIdx = np.where(vecData[l][:, 1] < 15)
        print(fIdx[0].shape[0])
        print(fIdx[0].shape[0] / 10000)
        vecData[l] = vecData[l][fIdx]

        print(np.min(vecData[l][:, 0]), np.max(vecData[l][:, 0]))
    

    #---------------Rank distributions------------------#
    if bHDists:
        for l in range(len(vecLangs)):
            strLang = vecLangs[l]
            nDist = np.zeros((15))
            nN = np.zeros((15))
            for dCC in vecFullData[l]:
                nDist[:len(dCC["NumCellsPerRank"])] += np.array(dCC["NumCellsPerRank"])
                nN[:len(dCC["NumCellsPerRank"])] += 1
            nDist /= nN

            plt.plot(np.arange(0, 15, 1), nDist, label = strLang, color = vecLangColors[l], linewidth = 3)

        plt.legend(fontsize = 26)
        plt.show()
        plt.close()



    #------------------Scalars-----------------------#
    maxX = 255
    iBinSize = 7
    vecXBins = [i for i in range(60)] + [60 + iBinSize*i for i in range((maxX - 60) // iBinSize)]

    for l in range(len(vecLangs)):
        strLang = vecLangs[l]

        X = np.sort(np.unique(vecData[l][:, 0]))
        Y = []
        YStd = []
        # for i in range(X.shape[0]):
        #     x = X[i]
        #     sIdx = np.where(vecData[l][:, 0] == x)
        #     Y.append(np.median(vecData[l][sIdx[0], 1]))
        #plt.plot(X, Y, label = strLang, linewidth = 3)

        for i in range(len(vecXBins) - 1):
            sIdx = np.where((vecData[l][:, 0] >= vecXBins[i]) & (vecData[l][:, 0] < vecXBins[i+1]))
            Y.append(np.mean(vecData[l][sIdx[0], idxY]))
            YStd.append(np.std(vecData[l][sIdx[0], idxY]))

            if bPlotStd:
                std = YStd[-1]
                plt.plot([vecXBins[i+1], vecXBins[i+1]], [Y[-1] - std, Y[-1] + std], color = "black")

        plt.plot(vecXBins[1:], Y, label = strLang, color = vecLangColors[l], linewidth = 3)

    plt.legend(fontsize = 26)
    plt.show()
    plt.close()

def main():
    PlotComplexScalars(N = 10000, idxY = 4, bHDists = True)


if __name__ == "__main__":
    main()