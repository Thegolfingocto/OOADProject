from datasets import load_dataset 
import os

strDataset = "codeparrot/github-code"
vecLangs = ["Java", "C++"]
N = 5
MIN_SIZE = 100000
strSaveDir = "../CodeExamples/"

if __name__ == "__main__":
    hfDS = load_dataset(strDataset, split = "train", streaming = True)
    vecSamples = [[] for _ in range(len(vecLangs))]

    for dSample in hfDS:
        if dSample["language"] not in vecLangs: continue
        if dSample["size"] < MIN_SIZE: continue
        idx = vecLangs.index(dSample["language"])
        if len(vecSamples[idx]) == N: continue
        vecSamples[idx].append(dSample["code"])
        print([len(vecS) for vecS in vecSamples])
        if min([len(vecS) for vecS in vecSamples]) >= N: break

    if not os.path.exists(strSaveDir):
        os.mkdir(strSaveDir)

    for strLang in vecLangs:
        if not os.path.exists(strSaveDir + strLang + "/"):
            os.mkdir(strSaveDir + strLang + "/")

        idx = vecLangs.index(strLang)
        
        for i in range(N):
            strSavePath = strSaveDir + strLang + "/" + str(i).zfill(4) + ".txt"
            with open(strSavePath, "w") as f:
                f.write(vecSamples[idx][i])
