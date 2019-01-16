#grader.py
#Will Baxley, 1/18/8
#Context Lab, Dartmouth College, Hanover, NH

# reads "testdata" and cleanly outputs which questions the user got correct

# performs the desired analysis on a given file
def gradefile(filename):
    infile = open(filename, "r")
    lines = infile.read().split("\n")
    print(lines[1])
    infile.close()

gradefile("testdata")