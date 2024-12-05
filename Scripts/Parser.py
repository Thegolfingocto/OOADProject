import re
import numpy as np
import os
import json

vecLangs = ["Java", "C++", "Rust"]

mapLangToPattern = {
    "Java": r'\b(?:public|private|protected)?\s*(?:static\s*)?(?:[\w<>\[\]]+\s+)+(\w+)\s*\([^)]*\)\s*(?:throws\s*\w+)?\s*\{',
    "C++": r'\b([a-zA-Z0-9_]\w*)\s*\([^;)]*\)\s*\{',
    "Rust": r'\b\s*(?:fn\s*)([a-zA-Z0-9_]\w*)\s*\([^;)]*\)\s*(?:->\s*)?[^;{]*\s*\{',
}

regIsFunc = r'\b[a-zA-Z0-9_.->]+\('

vecMathOps = ["+", "-", "/", "*", "%", "//", "**"]
vecNotFuncs = ["if", "while", "for", "new", "do"]

mapBraceTypes = {
    "{": "}",
    "(": ")",
    "[": "]",
}

def FindClosingBrace(code, start_index, chType: str = '{') -> int:
    assert(code[start_index] == chType)
    chEndType = mapBraceTypes[chType]
    brace_count = 1
    for i in range(start_index + 1, len(code)):
        if code[i] == chType:
            brace_count += 1
        elif code[i] == chEndType:
            brace_count -= 1
        if brace_count == 0:
            return i
    return None

def FindFunctionCalls(strLine: str) -> list[str]:
    vecCalledFunctionNames = []
    for match in re.finditer(regIsFunc, strLine):
        idxStart = match.start()
        idxNameEnd = match.end() - 1
        idxCallEnd = FindClosingBrace(strLine, idxNameEnd, chType = '(')

        if not idxCallEnd:
            #print("Warning! Could not find end of function call:", strLine)
            idxCallEnd = len(strLine) - 1

        strName = strLine[idxStart:idxNameEnd]

        strCall = strLine[idxNameEnd:idxCallEnd + 1]

        #avoid duplicates
        if strName in vecCalledFunctionNames: continue

        #if multiple params, it is definitely a function
        #otherwise, if there are no math operations or warning tokens, it is 'probably' not a complex equation or conditional
        if any(notfunc in strLine for notfunc in vecNotFuncs): continue
        
        if ',' in strCall:
            vecCalledFunctionNames.append(strName)
            continue

        if not any(op in strCall for op in vecMathOps):
            vecCalledFunctionNames.append(strName)
            continue

        #print("Function Name:", strLine[idxStart:idxNameEnd])
        #print("Function Params:", strLine[idxNameEnd:idxCallEnd + 1])

    return vecCalledFunctionNames

def FindFunctions(strCode: str, strL: str = "Java") -> dict:
    regPattern = mapLangToPattern.get(strL)
    dFunctions = {}

    #main function extraction loop
    for match in re.finditer(regPattern, strCode):
        strFunctionName = match.group(1)

        if strFunctionName in vecNotFuncs: continue

        idxStart = match.start()
        iStartLine = strCode.count('\n', 0, idxStart) + 1
        
        idxEnd = FindClosingBrace(strCode, match.end() - 1)
        if not idxEnd: continue
        #print(strFunctionName, strCode[idxStart : idxEnd + 1])
        #input()
        iEndLine = strCode.count('\n', 0, idxEnd) + 1

        if not iEndLine:
            print("Error! Could not find closing brace for function at line:", iStartLine)
            continue

        if strFunctionName not in dFunctions.keys():
            dFunc = {
                "StartLine": iStartLine,
                "EndLine": iEndLine,
                "Body": strCode[idxStart : idxEnd + 1].splitlines(),
                "Callees": [],
                "SubCallees": [],
                "Callers": [],
                "Rank": -1,
            }
            dFunctions[strFunctionName] = dFunc
        else:
            #print("Warning! Found duplicate function declaration:", strFunctionName)
            continue
    
    #collect all names in a list for callee mapping
    vecFunctionNames = [key for key in dFunctions.keys()]
    dSubFunctions = {} #keep track of which functions are external to the source file in question

    #callee processing loop
    for strFunctionName in vecFunctionNames:
        vecCalleeNames = []
        for strLine in dFunctions[strFunctionName]["Body"]:
            vecCalleeNames += FindFunctionCalls(strLine) #collect all called functions

        while strFunctionName in vecCalleeNames: vecCalleeNames.remove(strFunctionName) #don't count the function itself

        #process caller/callee relationships
        for strCalleeName in vecCalleeNames:
            bSubFunc = strCalleeName not in vecFunctionNames
            if bSubFunc:
                #add the subfunction if necessary
                if not strCalleeName in dSubFunctions.keys():
                    dSubFunc = {
                        "Callers": [],
                        "Rank": 0,
                    }
                    dSubFunctions[strCalleeName] = dSubFunc

                if not strCalleeName in dFunctions[strFunctionName]["SubCallees"]: dFunctions[strFunctionName]["SubCallees"].append(strCalleeName)
                if not strFunctionName in dSubFunctions[strCalleeName]["Callers"]: dSubFunctions[strCalleeName]["Callers"].append(strFunctionName)

            else:
                if not strCalleeName in dFunctions[strFunctionName]["Callees"]: dFunctions[strFunctionName]["Callees"].append(strCalleeName)
                if not strFunctionName in dFunctions[strCalleeName]["Callers"]: dFunctions[strCalleeName]["Callers"].append(strFunctionName)

    return {
        "Functions": dFunctions,
        "SubFunctions": dSubFunctions
    }

def AssignRank(strKey: str, dUniverse: dict, vecAlreadyVisited: list[str] = [], iDepth: int = 0, dKeyToDepth: dict = {}) -> None:
    if dUniverse[strKey]["Rank"] != -1: return

    #functions w/ no calls are rank 0. functions w/ only sub-callees are rank 1. These form the base cases of the recursion.
    if len(dUniverse[strKey]["Callees"]) == 0:
        if len(dUniverse[strKey]["SubCallees"]) == 0:
            dUniverse[strKey]["Rank"] = 0
        else:
            dUniverse[strKey]["Rank"] = 1
        return
    
    iMaxR = 0
    iLoopR = 0
    #print(strKey, dUniverse[strKey]["Callees"], vecAlreadyVisited if len(vecAlreadyVisited) < 6 else len(vecAlreadyVisited))
    for strK in dUniverse[strKey]["Callees"]:
        #prevent infinite recursions due to recursions/loops...lmao
        if strK in vecAlreadyVisited:
            iLoopR = max([iLoopR, iDepth - dKeyToDepth[strK] + 2]) #size of the function loop
            print("Found loop of depth:", iLoopR)
            continue

        if strKey not in vecAlreadyVisited: vecAlreadyVisited.append(strKey)
            
        if strKey not in dKeyToDepth.keys(): dKeyToDepth[strKey] = iDepth
        else: dKeyToDepth[strKey] = max([iDepth, dKeyToDepth[strKey]])

        AssignRank(strK, dUniverse, vecAlreadyVisited, iDepth + 1, dKeyToDepth) #recurse downwards w.r.t rank
        iMaxR = max([iMaxR, dUniverse[strK]["Rank"]])

    dUniverse[strKey]["Rank"] = iMaxR + iLoopR + 1

    return

def BuildCC(dParseData: dict) -> dict:
    '''
    This function accepts output from FindFunctions() and builds a combinatorial complex
    '''
    dFunctions = dParseData["Functions"]
    dSubFunctions = dParseData["SubFunctions"]
    mapRankToCells = [list(dParseData["SubFunctions"].keys()), []] #it is 'essentially guarenteed' that rank 0 and 1 cells exist

    #compute rank function and associated partitioning
    for strKey in dFunctions.keys():
        AssignRank(strKey, dFunctions)
        while (len(mapRankToCells)) < dFunctions[strKey]["Rank"] + 1: mapRankToCells.append([])
        mapRankToCells[dFunctions[strKey]["Rank"]].append(strKey)

    #these tensors store +/- 1 adjacency relations
    vecAdj = [np.zeros((len(mapRankToCells[i]), len(mapRankToCells[i]), 2)) for i in range(len(mapRankToCells))]
    vecInc = [np.zeros((len(mapRankToCells[i]), len(mapRankToCells[i+1]))) for i in range(len(mapRankToCells) - 1)]

    #compute up-adj
    for r in range(1, len(mapRankToCells)):
        strQ = "SubCallees" if r == 1 else "Callees"
        dQ = dSubFunctions if r == 1 else dFunctions
        for cell in mapRankToCells[r]:
            for i in range(len(dFunctions[cell][strQ])):
                if dQ[dFunctions[cell][strQ][i]]["Rank"] != r - 1: continue

                for j in range(i + 1, len(dFunctions[cell][strQ])):
                    if dQ[dFunctions[cell][strQ][j]]["Rank"] != r - 1: continue

                    idx1 = mapRankToCells[r - 1].index(dFunctions[cell][strQ][i])
                    idx2 = mapRankToCells[r - 1].index(dFunctions[cell][strQ][j])
                    vecAdj[r - 1][idx1, idx2, 0] = 1
                    vecAdj[r - 1][idx2, idx1, 0] = 1

    #compute down-adj
    for r in range(len(mapRankToCells) - 1):
        dQ = dSubFunctions if not r else dFunctions
        for cell in mapRankToCells[r]:
            if not r and cell not in dQ.keys(): dQ = dFunctions #switch to the other dict halfway thru b/c rank 0 cells are guarenteed to be ordered nicely
            for i in range(len(dQ[cell]["Callers"])):
                if dFunctions[dQ[cell]["Callers"][i]]["Rank"] != r + 1: continue

                idx1 = mapRankToCells[r + 1].index(dQ[cell]["Callers"][i])
                for j in range(i + 1, len(dQ[cell]["Callers"])):
                    if dFunctions[dQ[cell]["Callers"][j]]["Rank"] != r + 1: continue

                    
                    idx2 = mapRankToCells[r + 1].index(dQ[cell]["Callers"][j])
                    vecAdj[r + 1][idx1, idx2, 1] = 1
                    vecAdj[r + 1][idx2, idx1, 1] = 1

    #compute incidence
    for r in range(len(mapRankToCells) - 1):
        dQ = dSubFunctions if not r else dFunctions
        for cell in mapRankToCells[r]:
            if not r and cell not in dQ.keys(): dQ = dFunctions

            idx1 = mapRankToCells[r].index(cell)
            for i in range(len(dQ[cell]["Callers"])):
                if dFunctions[dQ[cell]["Callers"][i]]["Rank"] != r + 1: continue

                idx2 = mapRankToCells[r + 1].index(dQ[cell]["Callers"][i])
                vecInc[r][idx1, idx2] = 1

    return {
        "Functions": dFunctions,
        "SubFunctions": dSubFunctions,
        "RankMap": mapRankToCells,
    }, vecAdj, vecInc


def GetParseData(strLang: str, idx: int) -> dict:
    strInputPath = "../CodeExamples/" + strLang + "/" + str(idx).zfill(4) + ".txt"

    strOutputDir = "../ParseData/"
    if not os.path.exists(strOutputDir): os.mkdir(strOutputDir)
    strOutputDir += strLang + "/"
    if not os.path.exists(strOutputDir): os.mkdir(strOutputDir)
    strOutputPath = strOutputDir + str(idx).zfill(4) + ".json"

    if os.path.exists(strOutputPath):
        with open(strOutputPath, "r") as f:
            return json.load(f)

    if not os.path.exists(strInputPath):
        print("Error! Download file: {} before calling GetParseData()".format(strInputPath))
        return
    
    with open(strInputPath, "r") as f:
        dParseData = FindFunctions(f.read(), strLang)

    dParseData, vecAdj, vecInc = BuildCC(dParseData)
    mapRankToCells = dParseData["RankMap"]
    vecRankSizes = [len(mapRankToCells[i]) for i in range(len(mapRankToCells))]
    vecUpVolByRank = [float(np.sum(adj[:,:,0]) / (adj.shape[0] * adj.shape[1])) for adj in vecAdj]
    vecDownVolByRank = [float(np.sum(adj[:,:,1]) / (adj.shape[0] * adj.shape[1])) for adj in vecAdj]
    vecIncByRank = [float(np.sum(inc) / (inc.shape[0] * inc.shape[1])) for inc in vecInc]

    dFuncs = dParseData["Functions"]
    dSubFuncs = dParseData["SubFunctions"]

    dRet = {
        "Funcs": list(dFuncs.keys()),
        "FuncLines": [dFuncs[key]["EndLine"] - dFuncs[key]["StartLine"] for key in dFuncs.keys()],
        "FuncCalls": [len(dFuncs[key]["Callees"]) for key in dFuncs.keys()],
        "FuncCallers": [len(dFuncs[key]["Callers"]) for key in dFuncs.keys()],
        "SubFuncs": list(dParseData["SubFunctions"].keys()),
        "SubFuncCalls": [len(dFuncs[key]["SubCallees"]) for key in dFuncs.keys()],
        "SubFuncCallers": [len(dSubFuncs[key]["Callers"]) for key in dSubFuncs.keys()],

        "FuncsPerRank": mapRankToCells,
        "ComplexHeight": len(vecAdj),
        "NumCellsPerRank": vecRankSizes,
        "UpAdjVolPerRank": vecUpVolByRank,
        "DownAdjVolPerRank": vecDownVolByRank,
        "IncVolPerRank": vecIncByRank,
    }

    with open(strOutputPath, "w") as f:
        json.dump(dRet, f)

    return dRet

def Parse(strPath):
    strLang = ""
    for lang in vecLangs:
        if lang in strPath:
            strLang = lang
            break

    with open(strPath, "r") as f:
        dParseData = FindFunctions(f.read(), strLang)
    
    dParseData, vecAdj, vecInc = BuildCC(dParseData)
    mapRankToCells = dParseData["RankMap"]
    vecRankSizes = [len(mapRankToCells[i]) for i in range(len(mapRankToCells))]
    vecUpVolByRank = [float(np.sum(adj[:,:,0]) / (adj.shape[0] * adj.shape[1])) for adj in vecAdj]
    vecDownVolByRank = [float(np.sum(adj[:,:,1]) / (adj.shape[0] * adj.shape[1])) for adj in vecAdj]

    dFuncs = dParseData["Functions"]
    iSubFuncs = len(dParseData["SubFunctions"].keys())

    print("Parsing Results for Source File:", strPath)
    iSubCnt = 0
    fAvgSubFuncRatio = 0
    iCalleeFuncs = 0
    for strName in dFuncs.keys():
        print("Function:", strName)
        print("Lines:", dFuncs[strName]["StartLine"], "-->", dFuncs[strName]["EndLine"])
        print("Callees:", dFuncs[strName]["Callees"])
        print("Callers:", dFuncs[strName]["Callers"])
        print("Rank:", dFuncs[strName]["Rank"])
        print("Number of SubCallees:", len(dFuncs[strName]["SubCallees"]))
        iSubCnt += len(dFuncs[strName]["SubCallees"])
        if len(dFuncs[strName]["SubCallees"]) or len(dFuncs[strName]["Callees"]):
            fAvgSubFuncRatio += len(dFuncs[strName]["SubCallees"]) / (len(dFuncs[strName]["SubCallees"]) + len(dFuncs[strName]["Callees"]))
            iCalleeFuncs += 1
        print("-----------------------------------------")
        #input()
    
    print("Total Functions:", len(dFuncs.keys()))
    print("Percentage of Functions w/ Calls: {:.2f}%".format((iCalleeFuncs / len(dFuncs.keys())) * 100))
    print("Total Unique SubFunctions:", iSubFuncs)
    print("Total SubFunction Calls:", iSubCnt)
    print("SubFunction Uniqueness Percentage: {:.2f}%".format(iSubFuncs * 100 / iSubCnt))
    print("Average SubFunction Call Percentage: {:.2f}%".format(fAvgSubFuncRatio * 100 / iCalleeFuncs))
    print("Volume of +1-Adjacency:", vecUpVolByRank)
    print("Volume of -1-Adjacency:", vecDownVolByRank)
    print("Complex Height:", len(vecAdj))
    print("Rank Sizes:", vecRankSizes)
    print("Complex Volume:", np.sum(np.array([(i+1) * len(mapRankToCells[i]) for i in range(len(mapRankToCells))])) / np.sum(np.array(vecRankSizes)))

if __name__ == "__main__":
    Parse("../CodeExamples/Rust/0042.txt")