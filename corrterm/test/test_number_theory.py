import nose
from qc import *
from number_theory import *


def test_abs():
    assert abs(5) == 5
    assert abs(0) == 0
    assert abs(-17) == 17
    assert abs(-34.0) == 34.0

@forall(tries=100, t=tuples(items=integers(low=-10000, high=10000), size=(2,2)))
def test_random_gcd(t):
    a, b = t
    g, p = gcd(a, b)
    x, y = p
    assert g >= 0
    assert divides(g, a)
    assert divides(g, b)
    assert a * x + b * y== g
    for d in range(min(a, b)+1):
        if divides(d, a) and divides(d, b):
            assert divides(d, g)

def test_divides():
    assert divides(10, 20)
    assert divides(10, 0)
    assert not divides(10, 11)
    assert not divides(0, 13)
    assert divides(0, 0)
    assert divides(-5, 5)

@forall(tries=20, t=tuples(items=integers(low=-20, high=20),size=(2, 2)))
def test_random_da(t):
    a, b = t
    q, r = div_alg(a, b)
    assert a == b * q + r
    assert b == 0 or abs(r) <= abs(b) // 2
