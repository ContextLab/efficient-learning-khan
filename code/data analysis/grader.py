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
            if len(qsets[set][i].split("\"")) >= 10:   # (ignoring irrelevant lines) DO I NEED THIS?
                qsets[set][i] = qsets[set][i].split("\"")[10].strip().replace("&#8217;", "\'")   #...and clean it up
        qsets[set] = qsets[set][1:]     # get rid of some junk

    asets.append(lines[2].split(":"))       # first set of 10 answers goes in asets[0]
    asets.append(lines[7].split(":"))       # second set of 10 answers goes in asets[1]
    asets.append(lines[12].split(":"))      # third set of 10 answers goes in asets[2]

    for set in range(3):            # go through each question set in qsets
        for i in range(len(asets[set])):    # go through each question in the set...
            if len(asets[set][i].split("\\")) > 1:  #(ignoring irrelevant lines)
                asets[set][i] = asets[set][i].split("\\")[1].strip(" \"").replace("&#8217;","\'")  #...clean it up
        asets[set] = asets[set][5:15]       # get rid of some junk

    infile.close()

    return (qsets, asets)

# read the file of questions and return dictionary of the form {question -> (question number, answer)}
def readquestions(filename):
    questiondict = {}

    infile = open(filename, "r")
    lines = infile.read().split("\n")

    for qv1 in range(15):   # for each question from video 1
        questiondict[lines[6 + 8*qv1].strip(" ")] = (qv1 + 1, lines[7 + 8*qv1].strip(" "))

    for qv2 in range(15):   # for each question from video 2
        questiondict[lines[129 + 8*qv2].strip(" ")] = (qv2 + 16, lines[130 + 8 * qv2].strip(" "))

    return questiondict

#output all the questions into a csv file with columns:
#  c1 = question number, c2 = 0 for fourforces and 1 for birthofstars, c3 = question text
def printquestions(filename, qdict):
    outfile = open(filename, "w")

    #print out each question with the appropriate information
    for question in qdict:
        vid1 = qdict.get(question)[0] <= 15    # whether it came from video 1
        entry = str(qdict.get(question)[0]) + ","
        if qdict.get(question)[0] <= 15:
            entry += "0,";
        else:
            entry += "1,";
        entry += question + "\n"
        outfile.write(entry)

    outfile.close()

# output to the desired file
def grade(output, questiondict, qsets, asets):
    outfile = open(output, "w")
    for set in range(3):
        outfile.write("QUESTION SET " + str(1 + set) + "\n")
        for question in range(10):
            if qsets[set][question] in questiondict:    # check if we have the question
                outfile.write("q" + str(questiondict[qsets[set][question]][0]) + ", ")
                if asets[set][question] == questiondict[qsets[set][question]][1]:   # check if the answer is right
                    outfile.write("right")
                else:
                    outfile.write("wrong")
                outfile.write("\n")
            else:
                outfile.write("error" + "/n")
    outfile.close()

# call methods defined above
#(qsets, asets) = parsedata("testdata", 0)
questiondict = readquestions("testvideoquestions")
printquestions("questions.csv", questiondict)

#grade("testoutput", questiondict, qsets, asets)
