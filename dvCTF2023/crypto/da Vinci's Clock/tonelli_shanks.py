#returns the 2 square root of {a} modulo {p}
def tonelli_shanks(a, p) :
    test = pow(a, (p-1)//2, p)
    if test == 0 :
        print(f'Multiple of {p}')
        return 0
    if test == (-1) :
        print(f"Quadratic Non-residue")
        return 0
    if (p+1)%4 == 0:
        r = pow(a, (p+1)//4, p)
        return r,(p-r)
    q, s = 1, 0
    aux = p-1
    while aux%2 == 0:
        aux = aux//2
        s += 1
    q = (p-1)//(2**s)
    z = 2
    while pow(z, (p-1)//2, p) != (p-1) :
        z += 1
    c = pow(z,q,p)
    r = pow(a, (q+1)//2, p)
    t = pow(a,q,p)
    m = s
    while (t%p) != 1 :
        i = 1
        while pow(t,2**i,p) != 1:
            i += 1
        b = pow(c,2**(m-i-1),p)
        t = (t*(b**2))%p
        r = (r*b)%p
    return r,(p-r)

import argparse

def main() :
    parser = argparse.ArgumentParser(description= "Solving r² = a [p], returns 2 square roots (r1, r2)")
    parser.add_argument("-a", "--a", type=str, help = "We are looking for square roots of a modulo p, 'a' integer", required=True)
    parser.add_argument("-p", "--p", type=str, help = "'p' is a prime number as the modulo", required= True)
    args = parser.parse_args()
    try :
        a = int(args.a)
        p = int(args.p)
    except :
        print("Inputs must be integers, please refer to the help")
        a, p = 0, 1
    res = tonelli_shanks(a, p)
    if type(res) != int :
        r1, r2 = res
        print("r1 = {}\nr2 = {}".format(r1,r2))

if __name__ == '__main__':
    main()
    