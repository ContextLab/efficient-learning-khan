#grader.py
#Will Baxley, 1/18/8
#Context Lab, Dartmouth College, Hanover, NH

# reads "testdata" and cleanly outputs which questions the user got correct

# performs the desired analysis on a given file
def parsedata(filename):
    qsets = []  # list of the 3 lists of questions
    asets = []  # list of the 3 lists of answers

    infile = open(filename, "r")
    lines = infile.read().split("\n")

    qsets.append(lines[1].split("{")) # first set of 10 questions goes in qsets[0]
    qsets.append(lines[6].split("{"))  # second set of 10 questions goes in qsets[1]
    qsets.append(lines[11].split("{"))  # third set of 10 questions goes in qsets[2]

    for set in range(3):         # for each question set in qsets
        for i in range(len(qsets[set])):          # for each question in the set, clean it up
            if len(qsets[set][i].split(":")) > 2:
                qsets[set][i] = qsets[set][i].split(":")[2].split(",")[0].strip(' \"')
        qsets[set] = qsets[set][1:]

    asets.append(lines[2].split(":"))
    asets.append(lines[7].split(":"))
    asets.append(lines[12].split(":"))

    for set in range(3):            # for each question set in qsets
        for i in range(len(asets[set])):
            asets[set][i] = asets[set][i].split(",")[0].strip("}\ \"")
        asets[set] = asets[set][5:15]

    infile.close()

    return (qsets, asets)

(qsets, asets) = parsedata("testdata")
for q in qsets[0]:
    print(q)
