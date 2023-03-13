from functools import reduce
from Crypto.Util.number import inverse, isPrime
import primefac
import gmpy2
from factordb.factordb import FactorDB

def factor_list_primefac(n) :
    # returns Pi, the list of the prime divisors of n with their multiplicity
    P = primefac.primefac(n)
    P_f = dict()
    for k in P :
        P_f[k] = P_f.get(k,0) + 1
    Pi = [[i,P_f[i]] for i in P_f]
    return Pi

def factor_list_factordb(n) : # Another possibility to get the factor of a number
    # returns Pi, the list of the prime divisors of n with their multiplicity
    f = FactorDB(n)
    f.connect()
    P_f = f.get_factor_from_api()
    Pi = [[int(val),mul] for val,mul in P_f]
    assert all(isPrime(val) for val,mul in Pi)
    return Pi

# Function to use in case of a smooth number as the totient of the modulus p
def Pohlig_Hellman(g: int, h: int, Pi: list[list[int]]) :
    #returns x | h = g^x [p] with Pi the list of the prime divisors of the totient of p with their multiplicity (factor_list returns Pi for a given integer)
    n = reduce(lambda x,y : x*y, [p[0]**p[1] for p in Pi])
    Gi = list()
    Hi = list()
    Xi = list()
    for i in range(len(Pi)) :
        Gi.append(pow(g,n//(Pi[i][0]**Pi[i][1]),n+1))
        Hi.append(pow(h,n//(Pi[i][0]**Pi[i][1]),n+1))
        #Xi.append(Pohlig_Hellman_prime_power(n+1, Pi[i][0], Pi[i][1], Gi[i], Hi[i]))
        #Using baby_giant_step in case Pohlig_Hellman_prime_power isn't working:
        Xi.append(baby_giant_step(Pi[i][0]**Pi[i][1],n+1,Gi[i],Hi[i]))
    Yi = [n//(p[0]**p[1]) for p in Pi]
    Zi = [inverse(Yi[k],Pi[k][0]**Pi[k][1]) for k in range(len(Pi))]
    x = sum(Xi[k]*Yi[k]*Zi[k] for k in range(len(Pi)))%n
    return x

# g must be a real generator of the field or errors can occurred, g=2 is more a default value than a real generator for a given p
# Faster than baby_giant_step algorithm for the same specific result (inputs are slightly different but the aim is the same)
def Pohlig_Hellman_prime_power(moduli: int, p: int, e: int, g: int, h: int) :
    X = [0]
    gamma = pow(g,p**(e-1),moduli)
    for k in range(e) :
        h_k = pow(inverse(g**X[k],moduli)*h, p**(e-1-k), moduli)
        d_k = baby_giant_step(p, moduli, gamma, h_k)
        X.append(X[k] + d_k*p**k)
    return X[-1]

def baby_giant_step(n: int,p: int,alpha: int,beta: int) :
    m = gmpy2.iroot(n,2)[0]+1 #Can be replace by math.sqrt(n) + 1 (not recommended)
    table = dict()
    for j in range(m) :
        alpha_j = pow(alpha,j,p)
        table[alpha_j] = j
    alpha_m = inverse(pow(alpha,m,p),p)
    gamma = beta
    for i in range(m) :
        if gamma in table :
            return i*m+table[gamma]
        gamma = (gamma*alpha_m)%p

import argparse

def main() :
    parser = argparse.ArgumentParser(description= "returns x | A = g^x [p]")
    parser.add_argument("-A", "--A", type=str, help = "We are looking for the possible exponent giving 'A' integer as A = g^x", required=True)
    parser.add_argument("-g", "--g",  type=str, help = "g is the generator used, it must be an integer", required=True)
    parser.add_argument("-p", "--p", type=str, help = "'p' is a prime number as the modulo", required= True)
    args = parser.parse_args()
    try :
        A = int(args.A)
        g = int(args.g)
        p = int(args.p)
    except :
        raise Exception("Inputs must be integers, please refer to the help")
    
    try :
        Pi = factor_list_factordb(p-1)
    except :
        Pi = factor_list_primefac(p-1)

    x = Pohlig_Hellman(g, A, Pi)
    print("x = {}".format(x))

if __name__ == '__main__':
    main()
