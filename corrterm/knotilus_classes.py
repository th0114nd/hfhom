# SURF 2013
# FILE: knotilus_classes.py
# AUTHOR: Laura Shou
# MENTOR: Professor Yi Ni
# 06.21.13


'''
This module defines the KEdgeClass, which is very similar to the EdgeClass 
from plink_load.

VertexClass, IntersectionClass, RegionClass, and VectorClass are imported from
plink_classes.py.
'''

from plink_classes import VectorClass, IntersectionClass, VertexClass, \
     RegionClass

class KEdgeClass():
    ''' 
    Informally, an KEdge object consists of 2 segments. 
    The two segments are (flexpt1 - intersection) and (intersection - flexpt2).
    The segments are not important however; the necessary information is the
    two flex points and the intersection on the KEdge.
    '''
    def __init__(self, index, point1, point2, points, intersection):
        self.index = index # index in gKEdges
        self.point1 = point1 # flex point (VertexClass)
        self.point2 = point2 # flex point (VertexClass)
        self.points = points # indicies for flex points (index1, index2)
        self.inter = intersection # IntersectionClass
        self.vertices = [point1, point2] 

    def draw(self, canvas, flip=False, height=560):
        '''Draw it in Tkinter, on canvas 'canvas'.'''
        if not flip:
            return canvas.create_line(self.point1.x, self.point1.y, \
                                      self.inter.x, self.inter.y, \
                                      self.point2.x, self.point2.y)
        else:
            return canvas.create_line(self.point1.x, height - self.point1.y, \
                                      self.inter.x, height - self.inter.y, \
                                      self.point2.x, height - self.point2.y)