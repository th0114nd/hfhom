# SURF 2013
# FILE: plink_classes.py
# 08.22.13


'''
This module creates Vertex, Edge, Intersection, and Region objects for a link
diagram from Plink. It can load an existing Plink txt file, or open the Plink
editor for the user to draw a link.

VertexClass, EdgeClass, IntersectionClass, and RegionClass objects are stored
in global variables gVertex, gEdge, gIntersection, and gRegion, respectively.
'''

import math, sys, plink
from fractions import Fraction

class VertexClass():
    def __init__(self, coords, index):
        self.coords = coords
        self.x = coords[0]
        self.y = coords[1]
        self.index = index # position (i.e. nth vertex)
        self.edges = []   # the 2 edges with this point as a vertex
        
    
    def draw(self, canvas, col=None, flip=False, height=560):
        '''
        Draw a circle around the point, fill color = 'col', on canvas 'canvas'.
        
        Useful for Knotilus:
        'flip' boolean is used to reflect figure upside down.
        'height' is only used to reflect the figure. 
        '''
        if not flip:
            return canvas.create_oval(self.x - 5, self.y - 5, \
                                      self.x + 5, self.y + 5, fill=col)
        else:
            return canvas.create_oval(self.x - 5, height - self.y - 5, \
                                      self.x + 5, height - self.y + 5, fill=col)
    
    def dist(self, other):
        '''Euclidean distance between 'self' and 'other'.'''
        return math.sqrt((self.x - other.x)**2 + \
                         (self.y - other.y)**2)

class IntersectionClass(VertexClass):
    def __init__(self, edge1, edge2, coords):
        self.under = edge1 # EdgeClass instance
        self.over = edge2 # EdgeClass instance
        self.coords = coords
        self.x = self.coords[0]
        self.y = self.coords[1]
    
class VectorClass():
    '''These are used as directed Edges.'''
    def __init__(self, xcoord, ycoord):
        self.x = xcoord
        self.y = ycoord
        self.magnitude = math.sqrt(self.x**2 + self.y**2)
    
    def dotp(self, other):
        '''Return dot product of self and other.'''
        return self.x * other.x + self.y * other.y
    
    def angle(self, other):
        '''
        Smallest angle between two vectors, using dot product formula
        cos(theta) = |a*b|/(|a||b|).
        '''
        if self.magnitude == 0 or other.magnitude == 0: # this is unlikely...
            return 0
        frac = self.dotp(other)/(self.magnitude * other.magnitude)
        if abs(abs(frac) - 1) < 0.0001: 
            # had to do this since frac could be something like 1.000001, which
            # gives a domain error for acos
            if frac >= 0: # cos(theta) = 1 => theta = 0
                return 0
            return math.pi # cos(theta) = -1 => theta = pi
        return math.acos(frac)
    
    def angle_ccw(self, other, ydir=-1):
        '''
        Return angle measured counterclockwise from VectorClass 'self' to
        VectorClass 'other'. Angle is in [0, 2pi).
        
        Optional argument ydir specifies whether the y-axis is upside down or
        right side up. 
        ydir = -1 => upside down y-axis (Plink, Tkinter)
        ydir = 1 => right side up y-axis (Knotilus)
        '''
        # To find the angle, we need to first figure out whether the other 
        # vector is on the ccw side or the cw side (i.e. the direction that gets 
        # you to 'other' first). If it's on the ccw side, all we have to do is 
        # use the angle method. If it's on the cw side, we just take 2pi - angle
        # from the angle method.
        
        # So to figure out whether it's on the ccw or cw side, we construct
        # a vector rotated pi/2 ccw from the self vector. This is guaranteed to 
        # be on the ccw side of the self vector. Taking the dot product of this
        # rotated vector with the other vector will tell us which side the other
        # vector is on - positive dot product => same side (ccw), while 
        # negative dot product => opposite side (cw).
        
        # get the angle measured ccw between self and the positive x-axis
        if self.y >= 0:
            theta = self.angle(VectorClass(1,0))
        else: # y < 0 => angle greater than pi, but self.angle will give acute
            theta = 2 * math.pi - self.angle(VectorClass(1,0))

        # rotate pi/2 ccw
        theta = theta + ydir*math.pi / 2. 
        # ydir = -1 => subtract b/c tkinter y-axis is upside down
        rot_vec = VectorClass(math.cos(theta), math.sin(theta))
        if other.dotp(rot_vec) >= 0: # positive dot product => same side
            return self.angle(other)
        return 2 * math.pi - self.angle(other) # neg dot product => opp. side
    
    def is_same_dir(self, other):
        '''
        Return True if vectors point in same direction (parallel),
        False if vectors point in opposite direction (parallel),
        and raises an error otherwise (not parallel).
        '''
        if abs(self.angle(other) - math.pi) < 0.00001:
            return False
        elif self.angle(other) < 0.00001:
            return True
        else:
            print self.angle(other)
            raise ValueError('vectors are not parallel')
    
class EdgeClass():
    def __init__(self, index, point_indices, point1, point2):
        self.points = point_indices # indices for point1 and point2 in gVertices
        self.vertices = [point1, point2]
        self.point1 = point1 # VertexClass instance
        self.point2 = point2 # VertexClass instance
        self.index = index # position (i.e. nth edge)
        self.inter = [] # list of all intersections on edge
        
    def intersection(self, other):
        '''Return intersection coords. Uses fraction class to prevent round-off
        error.'''    
        # new variables are just because that's what I used to solve in
        # Mathematica.
        a = self.point1.x
        b = self.point1.y
        c = self.point2.x
        d = self.point2.y
        
        e = other.point1.x
        f = other.point1.y
        g = other.point2.x
        h = other.point2.y
        if abs(c - a) < 0.000001: # vertical
            if abs(g - e) < 0.000001:
                raise ValueError('Lines are parallel (both vertical)')
            return float(a), float(h - f)/float(g - e) * float(a - e) + f
        if abs(g - e) < 0.000001:
            return float(g), float(d - b)/float(c - a) * float(g - a) + b
        m1 = Fraction(d - b, c - a)
        m2 = Fraction(h - f, g - e)
        if m1 == m2:
            raise ValueError('Lines are parallel')
        # Mathematica solving:
        # Solve[{y == (d - b)/(c - a) (x - a) + b, 
        # y == (h - f)/(g - e) (x - e) + f}, {x, y}]
        x = Fraction(b - f + e * m2 - a * m1, -m1 + m2)
        y = Fraction(-(b*c*f - a*d*f - b*f*g + d*f*g - b*c*h + a*d*h + b*e*h \
                    - d*e*h),-b*e + d*e + a*f - c*f + b*g - d*g - a*h + c*h)
        return float(x), float(y)
    
    def draw(self, canvas, flip=False, height=560):
        '''
        Draw edge in Tkinter, on canvas 'canvas'.
        
        Useful for Knotilus:
        'flip' boolean is used to reflect figure upside down.
        'height' is only used to reflect the figure. 
        '''
        if not flip:
            return canvas.create_line(self.point1.x, self.point1.y, \
                                      self.point2.x, self.point2.y)
        else:
            return canvas.create_line(self.point1.x, height-self.point1.y,\
                                      self.poitn2.x, height-self.point2.y)

class RegionClass():
    def __init__(self, vert_list, total_angle):
        self.vertices = vert_list # list of vertices/intersections (as objects)
        self.angle = total_angle 
        # angle sum - positive if CCW, negative if CW
        # pos/CCW => normal region, neg/CW => exterior region
        # This is actually the sum the exterior angles, which will be +/-2pi.
        # This is only used in plink_draw.py, so that the exterior region 
        # (entire link) is not shaded.
    
    def __eq__(self, other):
        '''
        Return True if 'self' and 'other' are the same region, False otherwise.
        Equal (same) regions are determined by having exact same vertices, just
        in some rotation (shift).
        '''
        num_vert = len(self.vertices)
        if num_vert != len(other.vertices) or not (self.vertices[0] in \
                                                   other.vertices):
            return False
        start = (other.vertices).index(self.vertices[0]) # get shift amount
        for (index, vertex) in enumerate(self.vertices):
            if vertex != other.vertices[(index+start) % num_vert]:
                return False
        return True
    
    def num_inter(self, other):
        '''
        Return number of shared intersections with gVertices 'other'.
        '''
        num = 0
        for vertex in self.vertices:
            if isinstance(vertex, IntersectionClass):
                if vertex in other.vertices:
                    num += 1
        return num
    
    def draw(self, canvas, color='blue', flip=False, height=560):
        '''
        Draw polygon in Tkiner, fill color 'color', on canvas 'canvas'.
        Note this isn't exactly useful if one of the regions is the exterior.
        (Then this method will just color in the whole drawing.)
        
        Useful for Knotilus:
        'flip' boolean is used to reflect figure upside down.
        'height' is only used to reflect the figure. 
        '''
        vertices = []
        if not flip:
            for ver in self.vertices:
                vertices.extend([ver.x, ver.y])
        else:
            for ver in self.vertices:
                vertices.extend([ver.x, height-ver.y])
        vertices = tuple(vertices)
        return canvas.create_polygon(vertices, fill=color)