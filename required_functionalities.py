"""This file is like a short engine. """
"""The main purpose is to store all required functions, to prevent the app.py to be fill with spam """


def createHovertemplate(hover_data, head_len=2):
    """ Generate a hovertemplate string for a 3d python dash graph.
    :param hover_data:  List of values which are displayed by hovering. Value names have to be part of data.columns
    :param head_len:    Specifies how many values displayed in headline. The rest will be in description list.
    :return:            Returns a string which can be used as a hovertemplate
    """
    result = ""
    count = 0
    for it in hover_data:
        if count < head_len:
            result += "%{customdata[" + str(count) + "]} <br>"
        if count == head_len:
            result += "<extra>" + it + " = %{customdata[" + str(count) + "]} <br>"
        if count > head_len:
            result += it + " = %{customdata[" + str(count) + "]} <br>"
        count += 1

    if count > head_len:
        result += "</extra>"
    else:
        result += "<extra></extra>"

    return result
