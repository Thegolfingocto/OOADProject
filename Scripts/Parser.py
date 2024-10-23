import os

vecTypes = ["bool", "boolean", "int", "integer", "float", "double", "void", "string", "char"]

def Parse(strPath):
    with open(strPath, "r") as f:
        vecLines = f.readlines()

    print(vecLines)



if __name__ == "__main__":
    Parse("../CodeExamples/Java/0003.txt")