# Caltech SURF 2013
# FILE: test_plink_classes.py
# 08.22.13

'''
Tests for plink_classes.py
'''

from plink_classes import *
import nose
from nose.tools import assert_raises

err = 0.00001 # error tolerance

#
# VertexClass tests
#
def test_vertex_dist():
    pt0 = VertexClass((100.5, 0.1), 0)
    pt1 = VertexClass((352.1, 543), 1)
    assert abs(pt0.dist(pt1) - 598.3669192059) < err
    assert abs(pt0.dist(pt1) - pt1.dist(pt0)) < err

#  
# EdgeClass tests
#
def test_edge_intersection():
    e1 = EdgeClass(0, (0, 1), 0, 0) # to be vertical line
    e2 = EdgeClass(1, (2, 3), 0, 0)
    e3 = EdgeClass(2, (4, 5), 0, 0)
    e12 = EdgeClass(3, (6, 7), 0, 0) # to be another vertical line
    e31 = EdgeClass(4, (0, 1), 0, 0) # to be parallel to e3
    e4 = EdgeClass(5, (0, 1), 0, 0) # to be horizontal line
    e1.point1 = VertexClass((100, 100), 0)
    e1.point2 = VertexClass((100, 50), 1)
    e12.point1 = VertexClass((451, 80), 6)
    e12.point2 = VertexClass((451, 30), 7)
    e2.point1 = VertexClass((40, 250), 2)
    e2.point2 = VertexClass((359, 403), 3)
    e3.point1 = VertexClass((559, 0), 4)
    e3.point2 = VertexClass((4, 10), 5)
    e31.point1 = VertexClass((32, 100), 8)
    e31.point2 = VertexClass((143, 98), 9)
    e4.point1 = VertexClass((30, 319), 10)
    e4.point2 = VertexClass((495, 319), 11)
    
    # check intersection w/ vertical line
    assert abs(e1.intersection(e2)[0] - 100) < err
    assert abs(e1.intersection(e2)[1] - 278.77742946) < err
    assert abs(e2.intersection(e1)[0] - 100) < err
    assert abs(e2.intersection(e1)[1] - e1.intersection(e2)[1]) < err
    
    # check intersection w/ horizontal line
    assert abs(e4.intersection(e1)[0] - 100) < err
    assert abs(e4.intersection(e1)[1] - 319) < err
    assert abs(e4.intersection(e1)[0] - e1.intersection(e4)[0]) < err
    assert abs(e4.intersection(e1)[1] - e1.intersection(e4)[1]) < err
    assert abs(e4.intersection(e2)[0] - 183.8627450980) < err
    assert abs(e4.intersection(e2)[1] - 319) < err
    assert abs(e2.intersection(e4)[0] - e4.intersection(e2)[0]) < err
    assert abs(e4.intersection(e2)[1] - e2.intersection(e4)[1]) < err
    
    # check parallel lines
    assert_raises(ValueError, e1.intersection, e12)
    assert_raises(ValueError, e12.intersection, e1)
    assert_raises(ValueError, e3.intersection, e31)
    assert_raises(ValueError, e31.intersection, e3)
                  
    # check normal kind of intersection
    assert abs(e2.intersection(e3)[0] - e3.intersection(e2)[0]) < err
    assert abs(e2.intersection(e3)[1] - e3.intersection(e2)[1]) < err
    assert abs(e2.intersection(e3)[0] + 443.5780035185) < err
    assert abs(e2.intersection(e3)[1] - 18.0644685318) < err

#
# VectorClass tests
#
v0 = VectorClass(0, 0)
v1 = VectorClass(100, 50.4)
v2 = VectorClass(-19.2, 18.1)
v3 = VectorClass(-20.1, -341.3)
v3p = VectorClass(10.05, 170.65) # parallel to v3
v2p = VectorClass(-76.8, 72.4) # parallel to v2

def test_vector_dotp():
    assert abs(v0.dotp(v1)) < err
    assert abs(v1.dotp(v0)) < err
    assert abs(v1.dotp(v2) + 1007.76) < err
    assert abs(v2.dotp(v1) - v1.dotp(v2)) < err
    assert abs(v0.dotp(v2)) < err

def test_vector_angle():
    assert abs(v0.angle(v1)) < err
    assert abs(v1.angle(v0)) < err
    assert abs(v1.angle(v2) - 1.91883) < err
    assert abs(v2.angle(v1) - v1.angle(v2)) < err
    assert abs(v1.angle(v3) - 2.09646) < err
    assert abs(v1.angle(v3) - v3.angle(v1)) < err
    assert abs(v2.angle(v3) - 2.26789) < err
    assert abs(v2.angle(v3) - v3.angle(v2)) < err

def test_vector_angle_ccw():
    assert abs(v1.angle_ccw(v2, -1) - 4.36436) < err
    assert abs(v1.angle_ccw(v2, 1) - v1.angle(v2)) < err
    assert abs(v1.angle_ccw(v2, -1) + v2.angle_ccw(v1, -1) - 2*math.pi) < err
    assert abs(v1.angle_ccw(v2, 1) + v2.angle_ccw(v1, 1) - 2*math.pi) < err
    
    assert abs(v3.angle_ccw(v1, -1) - 4.18672) < err
    assert abs(v3.angle_ccw(v1, 1) - v3.angle(v1)) < err
    assert abs(v3.angle_ccw(v1, -1) + v1.angle_ccw(v3, -1) - 2*math.pi) < err
    assert abs(v3.angle_ccw(v1, 1) + v1.angle_ccw(v3, 1) - 2*math.pi) < err
    
    assert abs(v2.angle_ccw(v3, -1) - 4.0153) < err
    assert abs(v2.angle_ccw(v3, 1) - v2.angle(v3)) < err
    assert abs(v2.angle_ccw(v3, -1) + v3.angle_ccw(v2, -1) - 2*math.pi) < err
    assert abs(v2.angle_ccw(v3, 1) + v3.angle_ccw(v2, 1) - 2*math.pi) < err
    
def test_vector_is_same_dir():
    assert v2.is_same_dir(v2p) == True
    assert v2p.is_same_dir(v2) == True
    assert v3.is_same_dir(v3p) == False
    assert v3p.is_same_dir(v3) == False
    
    assert_raises(ValueError, v1.is_same_dir, v2)
    assert_raises(ValueError, v2.is_same_dir, v3p)

#
# RegionClass tests
#
p1 = VertexClass((1,0),0)
p4 = VertexClass((1,1),1)
p3 = VertexClass((0,1),2)
p2 = VertexClass((0,0),3)
p5 = VertexClass((2,2),4)

def test_equality():
    r1 = RegionClass([p1,p2,p3,p4], 2*math.pi)
    r2 = RegionClass([p3,p4,p1,p2], 2*math.pi)
    r3 = RegionClass([p1,p2,p3,p5,p4], 2*math.pi)
    r4 = RegionClass([p1,p2,p5,p4], 2*math.pi)    
    assert r1 == r2
    assert r1 != r3
    assert r1 != r4
    assert r2 != r3
    assert r2 != r4
    assert r3 != r4
    assert r2 == r1

def test_num_inter():
    # edge number for intersectionClasses don't matter
    i1 = IntersectionClass(0, 1, (0, 0.5))
    i2 = IntersectionClass(0, 1, (0.5, 0.5))
    i3 = IntersectionClass(0, 1, (2, 0.5))
    r1 = RegionClass([p1, p2, i2, p3, p4, p5, i3], 2*math.pi)
    r2 = RegionClass([i1, p2, p3, p4], 2*math.pi)
    r3 = RegionClass([i1, p2, i2, p3, p5, i3, p1, p2], 2*math.pi)
    assert r1.num_inter(r2) == r2.num_inter(r1) == 0
    assert r1.num_inter(r3) == r3.num_inter(r1) == 2
    assert r2.num_inter(r3) == r3.num_inter(r2) == 1

# functions will also be tested (indirectly) in graph_quad.py

if __name__ == '__main__':
    nose.runmodule()
