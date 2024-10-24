import os
import re

vecTypes = ["bool", "boolean", "int", "integer", "float", "double", "void", "string", "char"]


def find_java_method_definitions(code):
    # Regular expression to match Java method definitions
    pattern_function = r'\b(?:public|private|protected)?\s*(?:static\s*)?(?:[\w<>\[\]]+\s+)+(\w+)\s*\([^)]*\)\s*\{(.*?)\}'
    # Find all matches using re.findall
    methods = re.findall(pattern_function, code, re.DOTALL)
    methods_linenumber = dict()
    methods_functionbody = dict()
    for match in re.finditer(pattern_function, code, re.DOTALL):
        start = match.start()
        line_number = code.count('\n', 0, start) + 1
        if match[1] not in methods_linenumber.keys():
            methods_linenumber[match[1]] = []
        if match[1] not in methods_functionbody.keys():
            methods_functionbody[match[1]] = []
        methods_linenumber[match[1]].append(line_number)
        methods_functionbody[match[1]].append(match[2])
    return methods_linenumber, methods_functionbody

def Parse(strPath):
    with open(strPath, "r") as f:
        methods_linenumber, methods_functionbody = find_java_method_definitions(f.read())
    for method_name in methods_functionbody:
        print(method_name,'\n\n', methods_functionbody[method_name], '\n\n\n')
#methods = find_java_method_definitions(java_code)
#print(methods)


if __name__ == "__main__":
    Parse("../CodeExamples/Java/0003.txt")