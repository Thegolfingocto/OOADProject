import numpy as np
import matplotlib.pyplot as plt
import tqdm

from Parser import *

vecLangs = ["Java", "C++", "Rust"]
vecLangColors = ["lime", "dodgerblue", "maroon"]
vecChannelNames = ["Number of Cells", "Complex Height", "Number of Sub-Cells", "Total Cells w/ Rank <= 2", "Total Cell w/ Rank > 2"]

def PlotComplexScalars(N: int = 10000, idxY: int = 1, bPlotStd: bool = False, bRDists: bool = False, bADists: bool = False, bIDists: bool = False,
                       ) -> None:
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
    if bRDists:
        for l in range(len(vecLangs)):
            strLang = vecLangs[l]
            nDist = np.zeros((15))
            nN = np.zeros((15))
            for dCC in vecFullData[l]:
                nDist[:len(dCC["NumCellsPerRank"])] += np.array(dCC["NumCellsPerRank"])
                nN[:len(dCC["NumCellsPerRank"])] += 1
            nN = np.where(nN == 0, 1, nN)
            nDist /= nN

            plt.plot(np.arange(0, 15, 1), nDist, label = strLang, color = vecLangColors[l], linewidth = 3)

        plt.xticks(np.arange(0, 15, 1), fontsize = 12)
        maxY = np.max(nDist)
        plt.yticks(np.arange(0, maxY * 1.1, int(maxY / 10)), fontsize = 12)
        plt.grid()

        plt.xlabel("Rank", fontsize = 20)
        plt.ylabel("Average Number of Cells", fontsize = 20)

        plt.title("Distribution of Cells vs. Rank", fontsize = 32)

        plt.legend(fontsize = 26)
        plt.show()
        plt.close()

    
    #---------------Adj. Volume distributions------------------#
    if bADists:
        for l in range(len(vecLangs)):
            strLang = vecLangs[l]

            nDistUp = np.zeros((15))
            nDistDown = np.zeros((15))

            nNUp = np.zeros((15))
            nNDown = np.zeros((15))

            for dCC in vecFullData[l]:
                nDistUp[:len(dCC["UpAdjVolPerRank"])] += np.array(dCC["UpAdjVolPerRank"])
                nNUp[:len(dCC["UpAdjVolPerRank"])] += 1

                nDistDown[:len(dCC["DownAdjVolPerRank"])] += np.array(dCC["DownAdjVolPerRank"])
                nNDown[:len(dCC["DownAdjVolPerRank"])] += 1

            nNUp = np.where(nNUp == 0, 1, nNUp)
            nNDown = np.where(nNDown == 0, 1, nNDown)

            nDistUp /= nNUp
            nDistDown /= nNDown

            plt.plot(np.arange(0, 15, 1), nDistUp, label = strLang + ": +1 Adj.", color = vecLangColors[l], linewidth = 3)
            plt.plot(np.arange(0, 15, 1)[1:], nDistDown[1:], label = strLang + ": -1 Adj.", color = vecLangColors[l], linewidth = 3, linestyle = "dashed")

        plt.xticks(np.arange(0, 15, 1), fontsize = 12)
        maxY = max([np.max(nDistUp), np.max(nDistDown)])
        print(maxY)
        plt.yticks((1000 * np.arange(0, maxY * 1.1, maxY / 10)).astype(np.int16) / 1000, fontsize = 12)

        plt.xlabel("Rank", fontsize = 20)
        plt.ylabel("Average Volume of +/-1 Adjacency Matrices", fontsize = 20)
        plt.grid()

        plt.title("Distribution of Average Adjacency Volumes vs. Cell Rank", fontsize = 32)

        plt.legend(fontsize = 26)
        plt.show()
        plt.close()


    #---------------Incidence distributions------------------#
    if bIDists:
        for l in range(len(vecLangs)):
            strLang = vecLangs[l]
            nDist = np.zeros((15))
            nN = np.zeros((15))
            for dCC in vecFullData[l]:
                nDist[:len(dCC["IncVolPerRank"])] += np.array(dCC["IncVolPerRank"])
                nN[:len(dCC["IncVolPerRank"])] += 1
            nN = np.where(nN == 0, 1, nN)
            print(nDist)
            nDist /= nN

            plt.plot(np.arange(0, 15, 1), nDist, label = strLang, color = vecLangColors[l], linewidth = 3)

        plt.xticks(np.arange(0, 15, 1), fontsize = 12)
        maxY = np.max(nDist)
        plt.yticks(np.arange(0, maxY * 1.1, int(maxY / 10)), fontsize = 12)
        plt.grid()

        plt.xlabel("Rank", fontsize = 20)
        plt.ylabel("Average Volume of Incidence Matrices vs. Rank", fontsize = 20)

        plt.title("Distribution of Average Incidence Volumes vs. Cells Rank", fontsize = 32)

        plt.legend(fontsize = 26)
        plt.show()
        plt.close()



    #------------------Scalars-----------------------#
    maxX = 255
    iBinSize = 7
    vecXBins = [i for i in range(50)] + [50 + 3*i for i in range((150 - 50) // 3)] + [150 + iBinSize*i for i in range((maxX - 150) // iBinSize)]

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

            vecData[l][vecData[l] != vecData[l]] = 0

            Y.append(np.nanmean(vecData[l][sIdx[0], idxY]) if sIdx[0].shape[0] > 0 else 0)
            YStd.append(np.std(vecData[l][sIdx[0], idxY]))

            if bPlotStd:
                std = YStd[-1]
                plt.plot([vecXBins[i+1], vecXBins[i+1]], [Y[-1] - std, Y[-1] + std], color = "black")

        plt.plot(vecXBins[1:], Y, label = strLang, color = vecLangColors[l], linewidth = 3)


    plt.xlabel(vecChannelNames[0], fontsize = 20)
    plt.ylabel(vecChannelNames[idxY], fontsize = 20)

    plt.xticks(np.arange(0, maxX * 1.05, int(maxX / 20)), fontsize = 12)
    #plt.yticks(np.arange(0, max(Y) * 1.05, int(max(Y) / 20)), fontsize = 12)
    #plt.yticks(np.arange(0, 9, 1), fontsize = 12)
    plt.grid()

    plt.title("Average Number of High-Rank Cells vs. Number of Total Cells", fontsize = 32)

    plt.legend(fontsize = 26)
    plt.show()
    plt.close()

def main():
    PlotComplexScalars(N = 10000, idxY = 4, bRDists = True, bADists = False, bIDists = True)


if __name__ == "__main__":
    main()