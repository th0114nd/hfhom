
def abs(n):
    return n if n >= 0 else -n

def gcd(a, b, xtra=True):
    '''Computes the gcd of a, and b: "The least positive integer g such
    that g | a, g | b, and if d | a, b then d | g, except for the case
    when a and b are 0. gcd(0, 0) = 0 is not positive". This routine
    also returns a pair of numbers u, v such that u * a + b * v = gcd(a, b).'''
    g, p = xgcd(abs(a), abs(b))
    if g < 0:
        p = [-p[0], -p[1]]
    if a < 0:
        p[0] = -p[0]
    if b < 0:
        p[1] = -p[1]

    if xtra:
        return abs(g), p
    else:
        return abs(g)

def xgcd(a, b):
    '''Used to find the gcd of positive numbers a, b and track the necessary
    solutions by flip flopping between a larger and smaller.
    Courtesy of rcampbel at umbc.edu/~rcampbel/Computers/Python/numbthy.html'''
    u1 = 1
    v1 = 0
    u2 = 0
    v2 = 1
    if b == 0:
        return a, [u1, v1]
    while True:
        quot = -(a // b)
        a = a % b
        u1 = u1 + quot * u2
        v1 = v1 + quot * v2
        if a == 0:
            return b, [u2, v2]
        quot = -(b // a)
        b = b % a
        u2 = u2 + quot * u1
        v2 = v2 + quot * v1
        if b == 0:
            return a, [u1, v1]

def divides(a, b):
    ''' Checks if a | b'''
    if a == 0:
        return b == 0
    else:
        return b % a == 0
def div_alg(a, b):
    ''' Computes q, r such that a = q * b + r with |r| < b/2.'''
    if b == 0:
        return 0, a
    b_pos = abs(b)
    a_pos = abs(a)
    q = a // b
    r1 = a % b
    r2 = a % -b
    if (abs(r1) <= abs(r2)):
        return q, r1
    else:
        return q + 1, r2
