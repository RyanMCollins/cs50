#include <cs50.h>
#include <stdio.h>
#include <math.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // Check for correct number of arguments
    if (argc != 4)
    {
        printf("Usage: ./resize f infile outfile\n");
        return 1;
    }

    // Assign arguments to variables
    float factor = atof(argv[1]);
    char *infile = argv[2];
    char *outfile = argv[3];

    // Check that factor is in the valid range
    if (factor <= 0 || factor > 100)
    {
        printf("Factor must be in the range (0.0, 100.0]\n");
        return 1;
    }

    // Open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 1;
    }

    // Open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 1;
    }

    // Read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf_in;
    fread(&bf_in, sizeof(BITMAPFILEHEADER), 1, inptr);

    // Read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi_in;
    fread(&bi_in, sizeof(BITMAPINFOHEADER), 1, inptr);

    // Create headers for outfile
    BITMAPFILEHEADER bf_out = bf_in;
    BITMAPINFOHEADER bi_out = bi_in;

    // Calculate padding in infile
    int padding_in = (4 - (bi_in.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // Resize image for growth factor
    if (factor >= 1)
    {
        // Round factor to nearest integer value
        factor = round(factor);

        // Resize width and height for outfile
        bi_out.biWidth = bi_in.biWidth * factor;
        bi_out.biHeight = bi_in.biHeight * factor;

        // Calculate padding for outfile
        int padding_out = (4 - (bi_out.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

        // Set size of image and outfile
        bi_out.biSizeImage = abs(bi_out.biHeight) * (bi_out.biWidth * sizeof(RGBTRIPLE) + padding_out);
        bf_out.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + bi_out.biSizeImage;

        // Write outfile's BITMAPFILEHEADER
        fwrite(&bf_out, sizeof(BITMAPFILEHEADER), 1, outptr);

        // Write outfile's BITMAPINFOHEADER
        fwrite(&bi_out, sizeof(BITMAPINFOHEADER), 1, outptr);

        for (int i = 0, biHeight = abs(bi_in.biHeight); i < biHeight; i++)
        {
            for (int j = 0; j < factor; j++)
            {
                for (int k = 0; k < bi_in.biWidth; k++)
                {
                    // Temporary storage
                    RGBTRIPLE triple;

                    // Read RGB triple from infile
                    fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

                    for (int m = 0; m < factor; m++)
                    {
                        // Write RGB triple to outfile
                        fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
                    }
                }

                // Add padding to outfile
                for (int k = 0; k < padding_out; k++)
                {
                    fputc(0x00, outptr);
                }

                // Return to start of line
                fseek(inptr, -bi_in.biWidth * sizeof(RGBTRIPLE), SEEK_CUR);
            }
            // Move to next line
            int inpt_line = bi_in.biWidth * sizeof(RGBTRIPLE) + padding_in;
            fseek(inptr, inpt_line, SEEK_CUR);
        }
    }
    // Resize image for shrinking factor
    else
    {
        // Calculate number of RGB triples for which to alternate (num_include and num_exclude)
        int num_include;
        int num_exclude;
        int int_factor = round(factor * 10);
        if (int_factor >= 5)
        {
            num_include = int_factor / (10 - int_factor);
            num_exclude = 1;
        }
        else
        {
            num_include = 1;
            num_exclude = (10 - int_factor) / int_factor;
        }

        // If one set of included and excluded triples exceeds the width of the infile, the image will be copied exactly
        if (bi_in.biWidth < (num_include + num_exclude))
        {
            num_include = 1;
            num_exclude = 0;
        }

        // Resize width and height for outfile
        bi_out.biWidth = bi_in.biWidth - (bi_in.biWidth / (num_include + num_exclude)) * num_exclude;
        bi_out.biHeight = abs(bi_in.biHeight) - (abs(bi_in.biHeight) / (num_include + num_exclude)) * num_exclude;
        bi_out.biHeight *= bi_in.biHeight / (abs(bi_in.biHeight));

        // Calculate padding for outfile
        int padding_out = (4 - (bi_out.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

        // Set size of image and outfile
        bi_out.biSizeImage = abs(bi_out.biHeight) * (bi_out.biWidth * sizeof(RGBTRIPLE) + padding_out);
        bf_out.bfSize = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER) + bi_out.biSizeImage;

        // Write outfile's BITMAPFILEHEADER
        fwrite(&bf_out, sizeof(BITMAPFILEHEADER), 1, outptr);

        // Write outfile's BITMAPINFOHEADER
        fwrite(&bi_out, sizeof(BITMAPINFOHEADER), 1, outptr);

        int row_include = 0;
        int include = 0;
        int exclude = 0;
        int wcount = 0;
        int hcount = 0;
        int width = bi_in.biWidth;
        int height = bi_out.biHeight;

        while (true)
        {
            // Reach end of line
            if (wcount == width)
            {
                // Add padding to outfile
                for (int i = 0; i < padding_out; i++)
                {
                    fputc(0x00, outptr);
                }

                // Move past padding to next line of infile
                fseek(inptr, padding_in, SEEK_CUR);

                wcount = 0;
                hcount += 1;
                row_include += 1;
                include = 0;
                exclude = 0;
            }
            // Have at least one more element in series to copy
            else if (include < num_include)
            {
                // Temporary storage
                RGBTRIPLE triple;

                // Read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

                // Write RGB triple to outfile
                fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);

                include += 1;
                wcount += 1;
            }
            // Have at least one more element in series to skip over
            else
            {
                // Move past excluded triple
                fseek(inptr, sizeof(RGBTRIPLE), SEEK_CUR);

                exclude += 1;
                wcount += 1;
            }

            // Have no more elements to exclude in series
            if (exclude == num_exclude)
            {
                include = 0;
                exclude = 0;
            }

            // Reach end of file
            if (hcount == abs(height))
            {
                return 0;
            }

            // Reach end of lines in series to include
            if (row_include == num_include)
            {
                // Move past excluded lines
                int inpt_line = bi_in.biWidth * sizeof(RGBTRIPLE) + padding_in;
                fseek(inptr, num_exclude * inpt_line, SEEK_CUR);

                row_include = 0;
            }
        }
    }

    fclose(inptr);
    fclose(outptr);
}