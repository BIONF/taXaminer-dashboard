import math
import numpy as np

"""This file is like a short engine. 
The main purpose is to store all required functions, to prevent the app.py 
to be filled with spam """


"""------------------------------------------------------------"""
"""-Everything that belongs taxa coloring or color generation.-"""
"""------------------------------------------------------------"""


def rgbStrToVec(color):
    """ Converts a hex color code string into a numpy 3 vector.
    :param color: Color code string. An example would be "#1A05FF".
    :return: Returns a numpy 3 vector with red green and blue value.
    """
    try:
        return np.array([int("0x" + color[1:3], 16),
                         int("0x" + color[3:5], 16),
                         int("0x" + color[5:7], 16)])
    except ... as error:
        # TODO Exchange print with common log function.
        print("Error: required_functionalities->rgbStrToVec():", error)
        return np.array([0, 0, 0])


def rgbVecToStr(c_vec):
    """ Converts a numpy 3 vector within int variables into a rbg hex color
    code string.
    :param c_vec: Numpy 3 vector within int variables between 0 and 255.
    :return: Returns a string with a hex color code.
    """
    try:

        if c_vec[0] < 0: c_vec[0] = 0;
        if c_vec[0] > 255: c_vec[0] = 255;

        if c_vec[1] < 0: c_vec[1] = 0;
        if c_vec[1] > 255: c_vec[1] = 255;

        if c_vec[2] < 0: c_vec[2] = 0;
        if c_vec[2] > 255: c_vec[2] = 255;

        return "#" + str(hex(c_vec[0]))[2:4].zfill(2) + \
               str(hex(c_vec[1]))[2:4].zfill(2) + \
               str(hex(c_vec[2]))[2:4].zfill(2)
    except ... as error:
        # TODO Exchange print with common log function.
        print("Error: required_functionalities->rgbVecToStr()", error)
        return "#000000"


def colorRampPalette(colors, n):
    """ Interpolate colors linearly to create a color palette.
    :param colors:  List with color hex strings which is based on.
    :param n:       Number of required colors. That effects the greatness
    of return list.
    :return:        Gives a list with hex color strings.
    """
    result = []
    c_len = len(colors)
    if c_len < 1:
        return []
    if c_len == 1:
        return colors * n
    if n == 1:
        return [colors[0]]

    step = (len(colors) - 1) / (n - 1)
    for i in range(0, n):
        if math.floor(step * i) == math.ceil(step * i):
            result.append(colors[math.floor(step * i)])
        else:
            v_color_a = rgbStrToVec(colors[math.floor(step * i)])
            v_color_b = rgbStrToVec(colors[math.ceil(step * i)])

            v_color = (v_color_a + (v_color_b - v_color_a) *
                       (step * i % 1)).astype(int)
            result.append(rgbVecToStr(v_color))

    return result


def qualitativeColours(n, color_root=None):
    """ Generates a color palette in order to be able to differentiate between
    individual taxa as well as possible.
    :param n:   Number of required colors.
    :param color_root a color hex string, which define the pole label color.
    :return:    Gives a list with hex color strings.
    """
    defauld_root = ["#DF0101", "#FFFF00", "#298A08", "#00FF00", "#01DFD7", "#0101DF", "#F781BE"]

    if color_root:
        try:
            color_root = color_root.split()

            # Simply data check, not valid against none hex letters.
            for i in color_root:
                if len(i) != 7 or i[0] != '#':
                    print("Error: required_functionalities->qualitiveColours: ", "ValueError: not a hex color string.")
                    color_root = defauld_root
                    break

        except ... as e:
            # TODO Exchange print with common log function.
            print("Error: required_functionalities->qualitiveColours: ", e)
            color_root = defauld_root
    else:
        color_root = defauld_root

    return colorRampPalette(color_root, n)


def SetCustomColorTraces(fig, custom_d_index):
    """ Manual update_traces() function for python dash figure,
        witch is simply write a custom variable into the marker color.
        This function is just a specific bug solution and only usable with
        Scatter3d traces.
    :param fig: Python dash scatter_3d figure witch should be updated.
    :param custom_d_index: Index of custom variable in the corresponding trace.
    Effects something like %customdata[i].
    :return: All updates are by reference, hence it returns void.
    """
    for trace in fig.data:
        try:
            trace['marker']['color'] = trace['customdata'][0][custom_d_index]
        except ... as error:
            # TODO Exchange print with common log function.
            print("Error: required_functionalities->updateColorTraces:", error)


