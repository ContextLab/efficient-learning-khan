#grader.py
#Will Baxley, 1/18/8
#Context Lab, Dartmouth College, Hanover, NH

# reads "testdata" and cleanly outputs which questions the user got correct

# parses the data file and returns, in ordered lists, the questions and answers
def parsedata(filename):
    qsets = []  # list of the 3 lists of questions
    asets = []  # list of the 3 lists of answers

    infile = open(filename, "r")
    lines = infile.read().split("\n")

    qsets.append(lines[1].split("{")) # first set of 10 questions goes in qsets[0]
    qsets.append(lines[6].split("{"))  # second set of 10 questions goes in qsets[1]
    qsets.append(lines[11].split("{"))  # third set of 10 questions goes in qsets[2]

    for set in range(3):         # go through each question set in qsets
        for i in range(len(qsets[set])):          # go through each question in the set...
            if len(qsets[set][i].split(":")) > 2:   # (ignoring irrelevant lines)
                qsets[set][i] = qsets[set][i].split(":")[2].split(",")[0].strip(' \"').replace("&#8217;","\'") # ...and clean it up
        qsets[set] = qsets[set][1:]     # get rid of some junk

    asets.append(lines[2].split(":"))       # first set of 10 answers goes in asets[0]
    asets.append(lines[7].split(":"))       # second set of 10 answers goes in asets[1]
    asets.append(lines[12].split(":"))      # third set of 10 answers goes in asets[2]

    for set in range(3):            # go through each question set in qsets
        for i in range(len(asets[set])):    # go through each question in the set
            asets[set][i] = asets[set][i].split(",")[0].strip("}\ \"").replace("&#8217;","\'")  # clean it up
        asets[set] = asets[set][5:15]       # get rid of some junk

    infile.close()

    return (qsets, asets)

(qsets, asets) = parsedata("testdata")
for set in asets:
    for q in set:
        print(q)
