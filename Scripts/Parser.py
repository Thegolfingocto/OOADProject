import os
import re

vecTypes = ["bool", "boolean", "int", "integer", "float", "double", "void", "string", "char"]


def find_java_method_definitions(code):
    # Regular expression to match Java method definitions
    pattern = r'\b(?:public|private|protected)?\s*(?:static\s*)?(?:[\w<>\[\]]+\s+)+(\w+)\s*\([^)]*\)\s*\{'
    
    # Find all matches using re.findall
    methods = re.findall(pattern, code)
    
    return methods

def Parse(strPath):
    with open(strPath, "r") as f:
        methods = find_java_method_definitions(f.read())
    print(methods)
#methods = find_java_method_definitions(java_code)
#print(methods)


if __name__ == "__main__":
    Parse("../CodeExamples/Java/0003.txt")