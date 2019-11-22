import sys
from cs50 import get_string
from string import ascii_uppercase, ascii_lowercase


def main():
    if len(sys.argv) != 2 or (not sys.argv[1].isalpha()):
        sys.exit("Usage: python vigenere.py k")

    plaintext = get_string("plaintext: ")

    print("ciphertext:", vigenere(plaintext, sys.argv[1]))


def vigenere(text, key):
    """
    text: string, plaintext to encrypt
    key: string, the cipher key to encrypt with
    returns: string, the encrypted text
    """
    cipherText = []
    keyIndex = 0

    for i in range(len(text)):
        if text[i].isalpha():
            cipherText.append(caesar(text[i], key[keyIndex]))
            keyIndex = (keyIndex + 1) % len(key)
        else:
            cipherText.append(text[i])

    return "".join(cipherText)


def caesar(letter, key):
    """
    letter: string, a single letter to encrypt
    key: string, the key
    returns: string, a caesar shift of key applied to letter
    """
    if letter.isupper():
        alphaList = ascii_uppercase
    else:
        alphaList = ascii_lowercase

    letter = ord(letter.lower()) - 97
    key = ord(key.lower()) - 97

    return alphaList[(key + letter) % 26]


if __name__ == "__main__":
    main()