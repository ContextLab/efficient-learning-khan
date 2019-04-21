
def questions_to_csv(fromfile, tofile):
    infile = open(fromfile, "r")
    outfile = open(tofile, "w")
    lines = infile.read().split("\n")

    for idx in range(15):  # for each question from video 1
        outfile.write(str(1 + idx) + "\t")  # question ID
        outfile.write("1")    # video ID
        for i in range(5):  # question, answer 1 (correct), answer 2, answer 3, and answer 4
            outfile.write("\t" + lines[6 + i + 8 * idx])
        outfile.write("\n")

    for idx in range(15):  # for each question from video 2
        outfile.write(str(16 + idx) + "\t")  # question ID
        outfile.write("2")    # video ID
        for i in range(5):  # question, answer 1 (correct), answer 2, answer 3, and answer 4
            outfile.write("\t" + lines[129 + i + 8 * idx])
        outfile.write("\n")

    for idx in range(10):  # for each question from the general knowledge section
        outfile.write(str(31 + idx) + "\t")  # question ID
        outfile.write("0")    # video ID (here "0" denotes general knowledge)
        for i in range(5):  # question, answer 1 (correct), answer 2, answer 3, and answer 4
            outfile.write("\t" + lines[251 + i + 7 * idx])
        outfile.write("\n")

questions_to_csv('../data analysis/testvideoquestions', '../data analysis/astronomyquestions.tsv');
