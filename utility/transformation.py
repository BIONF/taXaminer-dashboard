"""
This module covers additional methods for interactions with 3d plots
"""
import numpy as np


def rotate_z(x, y, z, theta):
    """
    Calculate 3d coordinates for a circular rotation of the scatterplot
    :param x: x coordinate
    :param y: y coordinate
    :param z: z coordinate
    :param theta: rotation step
    :return: triple of x,y,z coordinates
    """
    c = x+1j*y
    return np.real(np.exp(1j*theta)*c), np.imag(np.exp(1j*theta)*c), z

