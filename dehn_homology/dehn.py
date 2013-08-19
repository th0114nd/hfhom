from fractions import Fraction

def dL(p, q, i):
    '''Computes the ith correction term of lens space L(p, q) of the unknot with
    slope p/q. It coerces p > 0, and q > 0 except in the base case of the trivial lens,
    L(1, 0) ~=~ S^3. It also reduces p and q by their gcd to ensure relative primality.
    Based on arxiv.org/pdf/math/0110170v2.pdf '''
    # FIXME: memoize to reduce redundancy if a bottleneck.
    if p == 1 and i == 0:
        # d(S^3 =  L(1, 0), 0). I'm pretty sure, at least.
        return 0
    else:
        p = p if p >= 0 else -p
        q = q if q >= 0 else -q
        g = number_theory.gcd(p, q, xtra=False)
        p = p / g
        q = q / g
        r = p % q
        j = i % q
        summand = Fraction((2 * i + 1 - p - q) ** 2, 4 * p * q)
        return Fraction(-1, 4) + summand - dL(q, r, j)

def d(K, p, q, i):
    '''Computes the ith correction term for the Dehn surgery with slope
    p/q on the knot K. Based off of arxiv.org/pdf/math/1009.4720.pdf.'''
    if p <= 0:
        raise ValueError("Argument p (supplied {0}) must be positive.".format(p))
    if q <= 0:
        raise ValueError("Argument q = {0} must be positive.".format(q))
    if not 0 <= i < p:
        raise ValueError("Argument i = {0} must be between 0 and "
                         "p - 1 = {1} inclusive.".format(i, p - 1))
    n1 = int(i/q)
    n2 = int((p + q - 1 - i) / q)
    return dL(p, q, i) - 2 * max(V(K, n1), V(K, n1))

def V(K, n):
    '''For the floer chain complex of K, C = CFK^\iy(K), with ZZ/2ZZ coefficients,
    the translation map 
        U: C -> C, 
        [x, i, j] |-> [x, i-1, j-1] 
    is an isomorphism of chain complexes. We have two quotient chain complexes
    under consideration, A+(n) = C{i >= 0 or j >= n} and B+ = C{i >= 0}. v(n):
    A+(n) -> B+ is the natural projection map for each n \in ZZ. For U_inv = U^-1,
    We have the homology group H_*(B+) ~ F[U_inv] := T+.'''
