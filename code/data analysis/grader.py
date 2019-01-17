#grader.py
#Will Baxley, 1/18/8
#Context Lab, Dartmouth College, Hanover, NH

# reads "testdata" and cleanly outputs which questions the user got correct

# parses the data file and returns, in ordered lists, the questions and answers
def parsedata(filename, startingline):  # the first line of the file is line 0
    qsets = []  # list of the 3 lists of questions
    asets = []  # list of the 3 lists of answers

    infile = open(filename, "r")
    lines = infile.read().split("\n")[startingline:startingline+14]

    qsets.append(lines[1].split("{")) # first set of 10 questions goes in qsets[0]
    qsets.append(lines[6].split("{"))  # second set of 10 questions goes in qsets[1]
    qsets.append(lines[11].split("{"))  # third set of 10 questions goes in qsets[2]

    for set in range(3):         # go through each question set in qsets
        for i in range(len(qsets[set])):          # go through each question in the set...
            if len(qsets[set][i].split(":")) > 2:   # (ignoring irrelevant lines)
                                                    # ...and clean it up
                qsets[set][i] = qsets[set][i].split(":")[2].split(",")[0].strip(' \"').replace("&#8217;","\'")
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

# read the file of questions and return ordered lists of the questions and their answers
def readquestions(filename):
    orderedQs = []  # ordered questions, from 1-30 (where 16-30 correspond to video 2)
    orderedAs = []  # ordered answers(see above)

    infile = open(filename, "r")
    lines = infile.read().split("\n")

    for qv1 in range(15):   # for each question from video 1
        orderedQs.append(lines[6 + 8*qv1].strip(" "))
        orderedAs.append(lines[7 + 8*qv1].strip(" "))

    for qv2 in range(15):   # for each question from video 2
        orderedQs.append(lines[129 + 8*qv2].strip(" "))
        orderedAs.append(lines[130 + 8*qv2].strip(" "))

    for q in orderedAs:
        print(q)

def grade():
    return 0

readquestions("testvideoquestions")

(qsets, asets) = parsedata("testdata", 0)
(orderedQs, orderedAs) = readquestions()

# for set in range(3):
#     for q in asets[set]:
#         print(q)
#         print()
