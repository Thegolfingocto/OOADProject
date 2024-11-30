import os
import re


mapLangToPattern = {
    "Java": r'\b(?:public|private|protected)?\s*(?:static\s*)?(?:[\w<>\[\]]+\s+)+(\w+)\s*\([^)]*\)\s*(?:throws\s*\w+)?\s*\{',
    "C++": r'\b([a-zA-Z_]\w*)\s*\([^;]*\)\s*\{'
}

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

def FindFunctions(code, strL: str = "Java"):
    regPattern = mapLangToPattern.get(strL)
    methods = []
    methods_linenumber = dict()
    methods_functionbody = dict()
    methods_methodscalled = dict()
    for match in re.finditer(regPattern, code):
        start = match.start()
        line_number = code.count('\n', 0, start) + 1
        if match.group(1) not in methods_linenumber.keys():
            methods_linenumber[match.group(1)] = []
        if match.group(1) not in methods_functionbody.keys():
            methods_functionbody[match.group(1)] = []
        methods_linenumber[match.group(1)].append(line_number)
        end_pos = FindClosingBrace(code, match.end() - 1)
        if end_pos:
            full_function = code[start:end_pos + 1]
            methods_functionbody[match.group(1)].append(full_function)
        methods.append(match.group(1))
    for i in methods_functionbody:
        for method in methods:
            for j in range(len(methods_functionbody[i])):
                if method in methods_functionbody[i][j]:
                    if i not in methods_methodscalled.keys():
                        methods_methodscalled[i] = []
                    methods_methodscalled[i].append(method)
    return methods_linenumber, methods_functionbody, methods_methodscalled

def Parse(strPath):
    strLang = ""
    if "Java" in strPath: strLang = "Java"
    elif "C++" in strPath: strLang = "C++"

    with open(strPath, "r") as f:
        methods_linenumber, methods_functionbody, methods_methodscalled = FindFunctions(f.read(), strLang)
    for method_name in methods_functionbody:
        print(methods_linenumber[method_name][0], method_name, '\n', "Called Funcs:", len(methods_methodscalled[method_name]))
        for i in range(len(methods_methodscalled[method_name])):
            print(methods_methodscalled[method_name][i])
        print("-----------------------------------------")
        input()
    print(len(methods_functionbody))
    #print(methods_methodscalled)

#methods = find_java_method_definitions(java_code)
#print(methods)


if __name__ == "__main__":
    Parse("../CodeExamples/Java/0003.txt")