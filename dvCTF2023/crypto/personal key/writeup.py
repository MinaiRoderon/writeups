from Crypto.Util.number import isPrime
from functools import reduce
import random
import math
import subprocess
from pwn import *
import json

primes = []
def sieve(maximum=10000):
    marked = [False]*(int(maximum/2)+1)
    for i in range(1, int((math.sqrt(maximum)-1)/2)+1):
        for j in range(((i*(i+1)) << 1), (int(maximum/2)+1), (2*i+1)):
            marked[j] = True
    primes.append(2)
    for i in range(1, int(maximum/2)):
        if (marked[i] == False):
            primes.append(2*i + 1)
sieve()
primes = primes[:500] # The first 500 primes

# Creating a smooth number with the first 500 primes at disposal
n = 1491
p_smooth = 0
median = primes[len(primes)//2].bit_length()-1
nbr_of_primes = n//median
while p_smooth.bit_length() < n or not(isPrime(p_smooth)) or p_smooth.bit_length() > n+10: # n+15 empirical decision during debugging
    p_smooth = reduce(lambda x,y : x*y, random.sample(primes, k = nbr_of_primes))+1

#p_smooth = 154719943404171706604055732251563060479136515199754584923158109616046965037403706912398998212500126962484188969489865697961198671730865525225579264093752879315061093864733298804493722100527126346446902826292113345359383149782517099170605786436734077706528358759955851236316464073656862744783612663937811733466979300836872639011440620076402042668742786709631716674939802328016376569720503727691131438751004085673243322211337645924770637325271424364027
#assert p_smooth.bit_length() == 1493

r = remote('crypto.dvc.tf', 2000)
line = r.recvlines(20,2)
Alice = json.loads(line[-6][:-1].decode().replace("'",'"'))
Bob = json.loads(line[-3][:-1].decode().replace("'",'"'))
# You receive first the variables A,B,g,p,iv and message sent during their exchange.
A = Alice['A']
g = Alice['g']
p = Alice['p']
iv = Bob['iv']
message = Bob["message"]

"""
You send: {"g": 2, "A": <the A given by Leonard>, "p": p_smooth}
You receive a second B calculated with this modulus.
"""
def json_send(hsh) -> None :
    request = (json.dumps(hsh)+'\r\n').encode()
    r.send(request)
to_send = {'A' : A, 'g' : g, 'p' : p_smooth}
json_send(to_send)
received = json.loads(r.recvlines(2)[-1][:-1].decode().replace("'",'"'))
B = received['B']

"""
To retrieve the private key of Leonard's friend (privkey):
run: python3 Pohlig_Hellman.py -g 2 -A <B> -p <p_smooth>
"""
result = subprocess.Popen(f"python3 Pohlig_Hellman.py -g {g} -A {B} -p {p_smooth}".split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
Bob_privkey = int(result.stdout.read()[4:-1])
"""
OR
run:
from sage.all import *
Z = GF(p_smooth)
Bob_privkey = Z(B).log(g)
"""

# private key used to cipher the message during the previous exchange
private_key = pow(A,Bob_privkey,p)

"""
To decipher the message:
run: python3 decrypt.py -k <private_key> -iv <iv> -c <message>
"""
result = subprocess.Popen(f"python3 decrypt.py -k {private_key} -iv {iv} -c {message}".split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
flag = result.stdout.read()
if 'Please' in flag :
    print(f"g={g} isn't a generator of the field created by p_smooth.\nSo the discrete log of B find another possible value for Bob_privkey which isn't actually the one used by Bob.\nIt is not a problem from the algorithm here, please restart the writeup until it creates a suitable p_smooth.")
else :
    print("FLAG = {}".format(flag))
