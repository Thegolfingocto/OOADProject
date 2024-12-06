from datasets import load_dataset 
import os
import json


if __name__ == "__main__":
    if not os.path.exists("Config.json"):
        print("Error! Config.json missing!")
        quit()
    
    with open("Config.json", "r") as f:
        dCfg = json.load(f)

    strDataset = dCfg["Dataset"]
    vecLangs = dCfg["Langs"]
    MIN_SIZE = dCfg["MIN_SIZE"]
    N = dCfg["N"]
    strSaveDir = dCfg["SaveDir"]

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
