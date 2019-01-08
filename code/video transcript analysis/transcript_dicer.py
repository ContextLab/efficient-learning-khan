#transcript_dicer.py
#Will Baxley, 1/07/8
#Context Lab, Dartmouth College, Hanover, NH

# reads "fourforcestrans" and "birthofstarstrans" and outputs, in order,
# all the clusters of 15 consecutive lines within the text
# test

# performs the desired analysis on a given file
def dicefile(filename):
    infile = open(filename, "r")
    lines = infile.read().split("\n")
    n = len(lines)/2        # number of lines with text
    i = 1                   # current start of the window
    while i + 14 <= n:
        cluster = ""
        for int in range(15):
            cluster += lines[2 * (i + int) - 1] + " "
        print(cluster + "\n")
        i += 1          # shift the window over by 1
    infile.close()

dicefile("fourforcestrans")
dicefile("birthofstarstrans")