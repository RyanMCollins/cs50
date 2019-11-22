// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "dictionary.h"

// Represents number of children for each node in a trie
#define N 27

// Represents a node in a trie
typedef struct node
{
    bool is_word;
    struct node *children[N];
}
node;

int get_trie_index(int character);
int get_size(node *cell);
void free_nodes(node *cell);


// Represents a trie
node *root;

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize trie
    root = malloc(sizeof(node));
    if (root == NULL)
    {
        return false;
    }
    root->is_word = false;
    for (int i = 0; i < N; i++)
    {
        root->children[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    // Insert words into trie
    while (fscanf(file, "%s", word) != EOF)
    {
        // Index in word
        int word_index = 0;

        // Pointer to traverse trie
        node *trav = root;

        while (word[word_index] != 0)
        {
            // Find node child index that corresponds to that character/letter
            int trie_index = get_trie_index(tolower(word[word_index]));

            // If there is no node at this point in memory, create one
            if (trav->children[trie_index] == NULL)
            {
                // Initialize node
                trav->children[trie_index] = malloc(sizeof(node));

                // Move trav to the correct child node
                trav = trav->children[trie_index];
                if (trav == NULL)
                {
                    return false;
                }
                trav->is_word = false;
                for (int i = 0; i < N; i++)
                {
                    trav->children[i] = NULL;
                }
            }
            // Move trav to the correct child node
            else
            {
                trav = trav->children[trie_index];
            }

            word_index++;
        }

        trav->is_word = true;
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return get_size(root);
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    // Index in word
    int word_index = 0;

    // Pointer to traverse trie
    node *trav = root;

    while (word[word_index] != 0)
    {
        char letter = word[word_index];
        if (!isalpha(letter) && letter != '\'')
        {
            return false;
        }

        // Find node's child that corresponds to that character/letter
        int trie_index = get_trie_index(tolower(letter));

        // Move trav to child corresponding to the current letter
        trav = trav->children[trie_index];

        // If there is no node at this point in memory, break the loop
        if (trav == NULL)
        {
            return false;
        }

        word_index++;
    }

    if (trav->is_word == true)
    {
        return true;
    }
    else
    {
        return false;
    }
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    free_nodes(root);

    return true;
}

// Returns the integer index of the trie corresponding to the character supplied
int get_trie_index(int character)
{
    if (character == '\'')
    {
        return 26;
    }
    else
    {
        return character - 'a';
    }
}

// Returns the size of the dictionary
int get_size(node *cell)
{
    if (cell == NULL)
    {
        return 0;
    }

    // Generate accumulator variable
    int acc = 0;

    // Set accumulator to 1 if current node represents a word
    if (cell->is_word == 1)
    {
        acc = 1;
    }

    // Recursively call function for each child
    for (int i = 0; i < 27; i++)
    {
        node *newptr = cell->children[i];
        acc += get_size(newptr);
    }

    return acc;
}

// Free all memory in a dictionary
void free_nodes(node *cell)
{
    if (cell == NULL)
    {
        return;
    }

    // Recursively call function on all child nodes
    for (int i = 0; i < 27; i++)
    {
        node *newptr = cell->children[i];
        free_nodes(newptr);
    }

    // Free memory used for node
    free(cell);
}