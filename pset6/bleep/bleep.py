from cs50 import get_string
from sys import argv, exit


def main():
    # Check for the right number of args
    if checkArgs() == False:
        exit("Usage: python bleep.py dictionary")

    # Create a set to contain the banned words
    bannedWords = set()

    # Open text file with banned words to read
    rfile = open(argv[1], "r")

    # Iterate over each line of the file
    for line in rfile:
        # Add the word on each line to the set
        bannedWords.add(line.rstrip("\n").lower())

    # Close the file
    rfile.close()

    # Get message from user as a list
    print("What message would you like to censor?")
    message = get_string().split()

    # Iterate over words in list
    for i in range(len(message)):
        # If word is in banned words set
        if message[i].lower() in bannedWords:
            # Replace word with *
            message[i] = repeatString("*", len(message[i]))

    # Join words into a string and print
    print(" ".join(message))


def checkArgs():
    return len(argv) == 2


def repeatString(s, n):
    """
    s: string, a string to be repeated
    n: int, the number of times to repeat s
    returns: string, s repeated n times
    """
    repString = ""
    for i in range(n):
        repString += s

    return repString


if __name__ == "__main__":
    main()
