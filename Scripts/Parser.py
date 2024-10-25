import os
import re

vecTypes = ["bool", "boolean", "int", "integer", "float", "double", "void", "string", "char"]


def find_java_method_definitions(code):
    pattern_function = r'\b(?:public|private|protected)?\s*(?:static\s*)?(?:[\w<>\[\]]+\s+)+(\w+)\s*\([^)]*\)\s*\{(.*?)\}'
    #pattern_function = r'\b\w+\s+\**(\w+)\s*\([\w\s,]*\)\s*\{(.*?)\}'
    # Find all matches using re.findall
    # methods = re.findall(pattern_function, code, re.DOTALL)
    methods = []
    methods_linenumber = dict()
    methods_functionbody = dict()
    methods_methodscalled = dict()
    for match in re.finditer(pattern_function, code, re.DOTALL):
        start = match.start()
        line_number = code.count('\n', 0, start) + 1
        if match[1] not in methods_linenumber.keys():
            methods_linenumber[match[1]] = []
        if match[1] not in methods_functionbody.keys():
            methods_functionbody[match[1]] = []
        methods_linenumber[match[1]].append(line_number)
        methods_functionbody[match[1]].append(match[2])
        methods.append(match[1])
    for i in methods_functionbody:
        for method in methods:
            for j in range(len(methods_functionbody[i])):
                if method in methods_functionbody[i][j]:
                    if i not in methods_methodscalled.keys():
                        methods_methodscalled[i] = []
                    methods_methodscalled[i].append(method)
    return methods_linenumber, methods_functionbody, methods_methodscalled

def Parse(strPath):
    with open(strPath, "r") as f:
        methods_linenumber, methods_functionbody, methods_methodscalled = find_java_method_definitions(f.read())
    for method_name in methods_functionbody:
        print(method_name,'\n\n')#, methods_functionbody[method_name], '\n\n\n')
    #print(methods_methodscalled)
#methods = find_java_method_definitions(java_code)
#print(methods)


if __name__ == "__main__":
    Parse("../CodeExamples/C++/0003.txt")