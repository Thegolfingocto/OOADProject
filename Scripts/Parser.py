import re

vecLangs = ["Java", "C++"]

mapLangToPattern = {
    "Java": r'\b(?:public|private|protected)?\s*(?:static\s*)?(?:[\w<>\[\]]+\s+)+(\w+)\s*\([^)]*\)\s*(?:throws\s*\w+)?\s*\{',
    "C++": r'\b([a-zA-Z_]\w*)\s*\([^;]*\)\s*\{'
}

regIsFunc = r'\b[a-zA-Z0-9_.->]+\('

vecMathOps = ["+", "-", "/", "*", "%", "//", "**"]
vecNotFuncs = ["if", "while", "for", "new", "do"]

mapBraceTypes = {
    "{": "}",
    "(": ")",
    "[": "]",
}

def FindClosingBrace(code, start_index, chType: str = '{'):
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

def FindFunctionCalls(strLine: str):
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

def FindFunctions(strCode: str, strL: str = "Java"):
    regPattern = mapLangToPattern.get(strL)
    dFunctions = {}

    #main function extraction loop
    for match in re.finditer(regPattern, strCode):
        strFunctionName = match.group(1)

        idxStart = match.start()
        iStartLine = strCode.count('\n', 0, idxStart) + 1
        
        idxEnd = FindClosingBrace(strCode, match.end() - 1)
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
            }
            dFunctions[strFunctionName] = dFunc
        else:
            print("Warning! Found duplicate function declaration:", strFunctionName)
            continue
    
    #collect all names in a list for callee mapping
    vecFunctionNames = [key for key in dFunctions.keys()]
    vecSubFunctionNames = [] #keep track of which functions are external to the source file in question

    #callee processing loop
    for strFunctionName in vecFunctionNames:
        vecCalleeNames = []
        for strLine in dFunctions[strFunctionName]["Body"]:
            vecCalleeNames += FindFunctionCalls(strLine) #collect all called functions

        while strFunctionName in vecCalleeNames: vecCalleeNames.remove(strFunctionName) #don't count the function itself

        #sort
        for strCalleeName in vecCalleeNames:
            bSubFunc = strCalleeName not in vecFunctionNames
            if bSubFunc:
                if not strCalleeName in vecSubFunctionNames: vecSubFunctionNames.append(strCalleeName)
                if not strCalleeName in dFunctions[strFunctionName]["SubCallees"]: dFunctions[strFunctionName]["SubCallees"].append(strCalleeName)
            else:
                if not strCalleeName in dFunctions[strFunctionName]["Callees"]: dFunctions[strFunctionName]["Callees"].append(strCalleeName)

    return {
        "Functions": dFunctions,
        "SubFunctions": vecSubFunctionNames
    }

def Parse(strPath):
    strLang = ""
    for lang in vecLangs:
        if lang in strPath:
            strLang = lang
            break

    with open(strPath, "r") as f:
        dParseData = FindFunctions(f.read(), strLang)
    
    dFuncs = dParseData["Functions"]
    iSubFuncs = len(dParseData["SubFunctions"])

    print("Parsing Results for Source File:", strPath)
    iSubCnt = 0
    fAvgSubFuncRatio = 0
    iCalleeFuncs = 0
    for strName in dFuncs.keys():
        print("Function:", strName)
        print("Lines:", dFuncs[strName]["StartLine"], "-->", dFuncs[strName]["EndLine"])
        print("Callees:", dFuncs[strName]["Callees"])
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

if __name__ == "__main__":
    Parse("../CodeExamples/Java/0003.txt")