from sage.all import *
from libnum import *

def solve_modular(c, b, m):
    """
    Solve modular equation x*c = b (mod m)
    Handle the case where gcd(c, m) != 1
    """
    k = 1
    g = gcd(c, m)
    while True:
        if g == 1:
            s = (b * invmod(c, m)) % m
            return [i * m + s for i in range(k)]
        if b % g != 0:
            return []
        c //= g
        m //= g
        b //= g

        k *= g
        g = gcd(c, m)

def solve_quadratic(a, b, c, n):
    """
    Find roots of polynomial P(x) = ax**2 + bx + c modulo 2**n
    a is equal to 1 (P is a monic polynomial)
    b is even
    """
    m = 2**n

    if b % 2 == 0:
        r = -(c - (b//2) ** 2)
 
        if has_sqrtmod(r, {2: n}):
            roots = sqrtmod_prime_power(r, 2, n)
            return list(set(map(lambda x: (x + b//2) % m, roots)))
        else:
            return []
    else:
        return []

def coppersmith(p, n, N):
    """
    Given the n LSB bits of p, use the Coppersmith theorem and LLL algorithm
    to recover the MSB bits of p.
    """
    mod0 = 2**n
    (a, b, g) = xgcd(mod0, N)
    #x = var('x')
    #Ring = PolynomialRing(Zmod(N), 'x', implementation='NTL')
    f = Ring(a*p + x)
    roots = f.small_roots(X=2**(2048 - n), beta=0.5)

    for r in roots:
        kq = r + p * a
        q = gcd(N, int(kq))
        p = N//q

        if q != 1 and q != N:
            return (p, q)
    return (None, None)

if __name__ == '__main__':
    import sys
    
    e = int(sys.argv[1])
    N = int(sys.argv[2])
    dLow = int(sys.argv[3])
    try:
        k = int(sys.argv[4])
    except:
        k = 0

    n = dLow.bit_length()
    mod0 = 2**n
    d0 = dLow % mod0
    
    x = var('x')
    Ring = PolynomialRing(Zmod(N), 'x', implementation='NTL')
    
    a,b = (k,k+1) if k else (1, e+1)
    for k in range(a,b):

        s_solutions = solve_modular(k, 1 + k*N + k - e*d0, mod0)

        for s in s_solutions:
            p_solutions = solve_quadratic(1, -s, N, n)
            
            for p in p_solutions:
                
                (p, q) = coppersmith(p, n, N)
                if p is not None:
                    if a!=k :
                        print("k=", k)
                    print("p=", p)
                    print("q=", q)
                    sys.exit(0)