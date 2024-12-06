from Parser import *

def TestParsing():
    #load test codes and parse
    vecDataToTest = []
    with open("Tests/Test.cpp", "r") as f:
        vecDataToTest.append(FindFunctions(f.read(), "C++"))
    with open("Tests/Test.java", "r") as f:
        vecDataToTest.append(FindFunctions(f.read(), "Java"))
    with open("Tests/Test.rust", "r") as f:
        vecDataToTest.append(FindFunctions(f.read(), "Rust"))

    #validate each piece of test data
    for dParseData in vecDataToTest:
        #make sure all the functions were found
        assert("ExampleSubFunctionCall" in dParseData["SubFunctions"].keys())
        assert("ExampleFunctionCall" in dParseData["Functions"].keys())
        assert("main" in dParseData["Functions"].keys())

        #make sure the right function calls were found
        assert("ExampleFunctionCall" in dParseData["Functions"]["main"]["Callees"])
        assert("ExampleSubFunctionCall" in dParseData["Functions"]["main"]["SubCallees"])

    return

def TestComplexConstruction():
    #load test codes and parse, then build the CCs
    vecDataToTest = []
    with open("Tests/Test.cpp", "r") as f:
        vecDataToTest.append(BuildCC(FindFunctions(f.read(), "C++"))[0])
    with open("Tests/Test.java", "r") as f:
        vecDataToTest.append(BuildCC(FindFunctions(f.read(), "Java"))[0])
    with open("Tests/Test.rust", "r") as f:
        vecDataToTest.append(BuildCC(FindFunctions(f.read(), "Rust"))[0])

    #validate each piece of test data
    for dParseData in vecDataToTest:
        #make sure all the functions were found
        assert("ExampleSubFunctionCall" in dParseData["SubFunctions"].keys())
        assert("ExampleFunctionCall" in dParseData["Functions"].keys())
        assert("main" in dParseData["Functions"].keys())

        #make sure the correct ranks were assigned
        assert(dParseData["Functions"]["main"]["Rank"] == 1)
        assert(dParseData["Functions"]["ExampleFunctionCall"]["Rank"] == 0)
        assert(dParseData["SubFunctions"]["ExampleSubFunctionCall"]["Rank"] == 0)

if __name__ == "__main__":
    TestParsing()
    TestComplexConstruction()
    