import os
import re

vecTypes = ["bool", "boolean", "int", "integer", "float", "double", "void", "string", "char"]

def find_matching_brace(code, start_index):
    """Given a starting position after an opening brace `{`, find the matching closing brace `}`"""
    brace_count = 1
    for i in range(start_index + 1, len(code)):
        if code[i] == '{':
            brace_count += 1
        elif code[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return i
    return None

def find_java_method_definitions(code):
    pattern_function_java = r'\b(?:public|private|protected)?\s*(?:static\s*)?(?:[\w<>\[\]]+\s+)+(\w+)\s*\([^)]*\)\s*\{'
    pattern_function_cplusplus = r'\b([a-zA-Z_]\w*)\s*\([^;]*\)\s*\{'
    methods = []
    methods_linenumber = dict()
    methods_functionbody = dict()
    methods_methodscalled = dict()
    for match in re.finditer(pattern_function_cplusplus, code):
        start = match.start()
        line_number = code.count('\n', 0, start) + 1
        if match.group(1) not in methods_linenumber.keys():
            methods_linenumber[match.group(1)] = []
        if match.group(1) not in methods_functionbody.keys():
            methods_functionbody[match.group(1)] = []
        methods_linenumber[match.group(1)].append(line_number)
        end_pos = find_matching_brace(code, match.end() - 1)
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
    with open(strPath, "r") as f:
        methods_linenumber, methods_functionbody, methods_methodscalled = find_java_method_definitions(f.read())
    for method_name in methods_functionbody:
        print(method_name,'\n\n', methods_functionbody[method_name], '\n\n\n')
    print(len(methods_functionbody))
    #print(methods_methodscalled)

#methods = find_java_method_definitions(java_code)
#print(methods)


if __name__ == "__main__":
    Parse("../CodeExamples/C++/0001.txt")