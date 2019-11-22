from cs50 import get_int


def main():
    printPyramid(getHeight())


def getHeight():
    """
    return: int, height specified by the user
    """
    while True:
        height = get_int("Height: ")
        if height > 0 and height < 9:
            return height


def printPyramid(height):
    """
    height: int, the height of the pyramid to be produced
    prints a double half pyramid with two spaces in the middle
    """
    for num in range(1, height + 1):
        repeatChar(" ", height - num)
        repeatChar("#", num)
        repeatChar(" ", 2)
        repeatChar("#", num)
        print()


def repeatChar(c, n):
    """
    c: string, a character to be repeated
    n: int, the number of times to repeat c
    """
    for i in range(n):
        print(c, end="")


if __name__ == "__main__":
    main()