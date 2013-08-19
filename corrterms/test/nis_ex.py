from smith import *
from ndqf import *
import numpy as np

x = np.matrix([[-5, -2],
               [-2, -4]])

y = np.matrix([[-2, 1, 0, 0, 0],
               [1, -3, 1, 1, 0],
               [0, 1, -2, 0, 0],
               [0, 1, 0, -2, 1],
               [0, 0, 0, 1, -2]])

d, (u, v) = smith_normal_form(x)

D, (U, V) = smith_normal_form(y)

g = Hom_Group(d, v)
G = Hom_Group(D, V)
print g
print G
