from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""
    # sol = []

    # Split a and b on newlines
    a, b = a.split("\n"), b.split("\n")

    sol = compareListOfStrings(a, b)

    return sol


def sentences(a, b):
    """Return sentences in both a and b"""

    a, b = sent_tokenize(a), sent_tokenize(b)

    sol = compareListOfStrings(a, b)

    return sol


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""
    sol = []

    alen = len(a)
    blen = len(b)
    for ia in range(alen - n + 1):
        asub = a[ia:ia + n]

        for ib in range(blen - n + 1):
            bsub = b[ib:ib + n]

            if asub == bsub and asub not in sol:
                sol.append(asub)

    return sol


def compareListOfStrings(a, b):
    """Return strings that appear in both a and b"""
    sol = []

    for aline in a:
        for bline in b:
            if aline == bline and aline not in sol:
                sol.append(aline)
                b.remove(bline)
                break

    return sol
