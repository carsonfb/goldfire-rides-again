"""
    This program creates the GoldFire logo using the algorithm that the original version of
    GoldFire used.  I originally wrote them during my senior year of high school and
    freshman year of college (nearly 30 years ago); I'm sure they could be rewritten in a
    much better manner, but I'm trying to re-use as many algorithms from the original as
    possible.

    Instead of creating the logo in the program, it is being created and saved as a data
    file to minimize the startup time.  Since this doesn't change between executions,
    there is no reason to generate it each time.
"""

"""
    Setup the font.  The letter in the variable name is the letter in the font.  A 1 means
    that it is an upper-case letter and a 2 means that it is a lower-case letter.  This is
    the same naming and data as used in the original version.

    A 254 means the end of the line and a 255 means the end of the character.  This is no
    longer needed as it would be possible to just process each character in the list.
    However, in x86 Aseembly language (what the original GoldFire was mostly written in), if
    there was not an end character, the program would continue reading into other data or
    code fragments.
"""

F1 = [
    3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 254, 
    2, 14, 254, 
    1, 15, 254, 
    1, 5, 6, 7, 8, 9, 10, 11, 15, 254, 
    1, 4, 12, 15, 254, 
    1, 4, 13, 14, 254, 
    1, 4, 254, 
    1, 4, 254,
    1, 5, 6, 7, 8, 9, 10, 11, 12, 254, 
    1, 13, 254, 1, 13, 254, 
    1, 5, 6, 7, 8, 9, 10, 11, 12, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 254, 
    0, 5, 254, 
    0, 5, 254,
    0, 5, 254, 
    1, 2, 3, 4, 255
]

G1 = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 254, 
    1, 15, 254, 
    0, 15, 254, 
    0, 4, 5, 6, 7, 8, 9, 10, 11, 15, 254, 
    0, 3, 12, 15, 254, 0, 3, 13, 14, 254, 
    0, 3, 254, 0, 3, 254, 
    0, 3, 254, 
    0, 3, 254, 
    0, 3, 11, 12, 13, 14, 254, 
    0, 3, 10, 15, 254, 
    0, 3, 10, 15, 254, 
    0, 3, 11, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 4, 5, 6, 7, 8, 9, 10, 11, 15, 254, 
    0, 15, 254, 
    1, 14, 254, 
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 255
]

D2 = [
    11,12,13,14,254,
    10,15,254,
    10,15,254,
    10,15,254,
    11,14,254,
    11,14,254,
    11,14,254,
    11,14,254,
    5,6,7,8,9,10,14,254,
    4,14,254,3,14,254,
    2,6,7,8,9,10,14,254,
    1,5,11,14,254,0,4,11,14,254,
    0,3,11,14,254,
    0,3,11,14,254,
    0,4,5,6,7,8,9,10,14,254,
    0,14,254,1,13,254,
    2,3,4,5,6,7,8,9,10,11,12,255
]

E2 = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 254, 
    1, 14, 254, 
    0, 15, 254, 
    0, 4, 5, 6, 7, 8, 9, 10, 11, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 4, 5, 6, 7, 8, 9, 10, 11, 15, 254, 
    0, 15, 254, 
    0, 14, 254, 
    0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 254, 
    0, 3, 254, 
    0, 3, 254, 
    0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 254, 
    0, 14, 254, 
    1, 14, 254, 
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 255
]

I2 = [
    1, 2, 254, 
    0, 3, 254, 
    0, 3, 254, 
    1, 2, 254, 
    254, 
    1, 2, 254, 
    0, 3, 254, 
    0, 3, 254, 
    0, 3, 254, 
    0, 3, 254, 
    0, 3, 254, 
    0, 3, 9, 10, 254, 
    0, 3, 8, 11, 254, 
    0, 3, 8, 11, 254, 
    0, 4, 5, 6, 7, 11, 254, 
    0, 11, 254, 
    1, 10, 254, 
    2, 3, 4, 5, 6, 7, 8, 9, 255
]

L2 = [
    1, 2, 3, 4, 254, 
    0, 5, 254, 
    0, 5, 254, 
    0, 5, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 254, 
    1, 4, 10, 11, 254, 
    1, 4, 9, 12, 254, 
    1, 4, 9, 12, 254, 
    1, 4, 9, 12, 254, 
    1, 5, 6, 7, 8, 12, 254, 
    1, 12, 254, 
    2, 11, 254, 
    3, 4, 5, 6, 7, 8, 9, 10, 255
]

O2 = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 254, 
    1, 14, 254, 
    0, 15, 254, 
    0, 4, 5, 6, 7, 8, 9, 10, 11, 15, 254, 
    0, 3, 12, 15, 254, 0, 3, 12, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 3, 12, 15, 254, 
    0, 4, 5, 6, 7, 8, 9, 10, 11, 15, 254, 
    0, 15, 254, 
    1, 14, 254, 
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 255
]

R2 = [
    1, 2, 3, 4, 5, 254, 
    0, 6, 254, 
    0, 6, 254, 
    1, 2, 7, 8, 9, 10, 11, 12, 13, 14, 254,
    3, 15, 254, 
    3, 16, 254, 
    3, 7, 8, 9, 10, 11, 12, 16, 254, 
    3, 6, 13, 16, 254, 
    3, 6, 14, 15, 254, 
    3, 6, 254, 
    3, 6, 254, 
    2, 7, 254, 
    2, 7, 254, 
    2, 7, 254, 3, 4, 5, 6, 255
]

def prn_bmp(character, char_pos, row, x_coord, char_data):
    """
        This function creates a bitmap for passed in character data.
    """

    for val in character:
        if val == 254:
            row += 1

        elif val != 255:
            char_data[row * 144 + char_pos * 18 + val + x_coord] = 128

    return char_data

def fill(char_data, x_pos, y_pos, color):
    """
        This function implements a rudimentary flood-fill algorithm.
    """

    start_color = char_data[y_pos * 18 * 8 + x_pos]

    char_data [y_pos * 18 * 8 + x_pos] = color

    if (x_pos - 1 >= 0) and (char_data [y_pos * 18 * 8 + x_pos - 1] == start_color):
        char_data = fill(char_data, x_pos - 1, y_pos, color)

    if (x_pos + 1 < 8 * 18) and (char_data [y_pos * 18 * 8 + x_pos + 1] == start_color):
        char_data = fill(char_data, x_pos + 1, y_pos, color)

    if (y_pos - 1 >= 0) and (char_data [(y_pos - 1) * 18 * 8 + x_pos] == start_color):
        char_data = fill(char_data, x_pos, y_pos - 1, color)

    if (y_pos + 1 < 20) and (char_data [(y_pos + 1) * 18 * 8 + x_pos] == start_color):
        char_data = fill(char_data, x_pos, y_pos + 1, color)

    return char_data

def shade(char_data, replace_color, new_color):
    """
        This function shades an area of the buffer with a gradient.
    """

    num_cols = len(char_data) // 20

    for row in range(0, 20):
        for col in range(0, num_cols):
            if char_data[row * num_cols + col] == replace_color:
                char_data[row * num_cols + col] = new_color

        new_color += 1

    return char_data

def create_string():
    """
        This function creates a string by calling prn_bmp repeatedly on all of the
        characters in a list.
    """

    goldfire = [0x00] * 18 * 8 * 20

    chars = [G1, O2, L2, D2, F1, I2, R2, E2]
    y_coords = [0, 5, 0, 0, 0, 2, 5, 4]
    x_coords = [0, 0, 0, 0, 0, 0, -2, 0]

    for pos, letter in enumerate(chars):
        goldfire = prn_bmp(letter, pos, y_coords[pos], x_coords[pos], goldfire)

    goldfire = fill(goldfire, 2, 1, 1)
    goldfire = fill(goldfire, 20, 7, 1)
    goldfire = fill(goldfire, 39, 1, 1)
    goldfire = fill(goldfire, 66, 1, 1)
    goldfire = fill(goldfire, 75, 1, 1)
    goldfire = fill(goldfire, 92, 3, 1)
    goldfire = fill(goldfire, 92, 8, 1)
    goldfire = fill(goldfire, 110, 6, 1)
    goldfire = fill(goldfire, 130, 6, 1)

    goldfire = shade(goldfire, 1, 52)

    return goldfire

index = 0
rows = 0

display = create_string()

for bit in display:
    index += 1

    if index == 18 * 8:
        index = 0
        rows += 1

with open("data/goldfire.bin", "wb") as gf_file:
    gf_file.write(bytes(display))
