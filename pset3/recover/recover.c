#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main(int argc, char *argv[])
{
    // Check that there is only 1 argument
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }

    // Open file to read from
    FILE *inptr = fopen(argv[1], "r");

    // Check that file is readable
    if (inptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not open %s.\n", argv[1]);
        return 1;
    }

    // Allocate 512 bytes for block
    uint8_t *block = malloc(512 * sizeof(uint8_t));

    // Create file number variable
    int file_number = -1;

    // Open infile as outptr as a temporary placeholder
    FILE *outptr = fopen(argv[1], "r");

    while (true)
    {

        // Read block head
        fread(block, 512, 1, inptr);

        // Exit if at end of infile
        if (feof(inptr))
        {
            fclose(outptr);
            free(block);
            fclose(inptr);
            return 0;
        }

        // If block head is start of new jpg, close outfile and open new outfile to write to
        char filename[7];
        if (block[0] == 255 && block[1] == 216 && block[2] == 255 && block[3] > 223 && block[3] < 240)
        {
            fclose(outptr);
            file_number++;

            sprintf(filename, "%03i.jpg", file_number);
            outptr = fopen(filename, "w");
        }

        // Move to next block if have not yet found a jpg
        if (file_number < 0)
        {
            fseek(inptr, 512, SEEK_CUR);
            continue;
        }

        // Check that file is writeable
        if (outptr == NULL)
        {
            fclose(inptr);
            free(block);
            fprintf(stderr, "Could not create %s.\n", filename);
            return 1;
        }

        // Write entire block to current outfile
        fwrite(block, 512, 1, outptr);
    }
}
