from cs50 import get_string


def main():
    num = getCardNum()

    type = getCardProvider(num)

    if type == "INVALID":
        print(type)
        return 0

    if checksum(num) == True:
        print(type)
    else:
        print("INVALID")


def getCardNum():
    """
    returns: user entered credit card number
    """
    while True:
        num = get_string("Number: ")
        if num.isnumeric():
            return num


def checksum(num):
    """
    num: string, credit card number
    returns: bool, True if the card number is valid, False otherwise
    """
    luhnNum = 0

    for i in range(len(num) - 2, -1, -2):
        double = 2 * int(num[i])
        luhnNum += (double % 10) + (double // 10)
    for i in range(len(num) - 1, -1, -2):
        luhnNum += int(num[i])

    if (luhnNum % 10) == 0:
        return True
    else:
        return False


def getCardProvider(num):
    """
    num: string, credit card number
    returns: string, "AMEX" "MASTERCARD" "VISA" or "INVALID"
    """
    if num[0] == "4" and (len(num) == 13 or len(num) == 16):
        return "VISA"
    elif (num[0:2] == "34" or num[0:2] == "37") and len(num) == 15:
        return "AMEX"
    elif num[0:2] in ["51", "52", "53", "54", "55"] and len(num) == 16:
        return "MASTERCARD"
    else:
        return "INVALID"


if __name__ == "__main__":
    main()