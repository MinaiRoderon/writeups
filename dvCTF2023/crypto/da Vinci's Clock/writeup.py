from Crypto.Cipher import AES
from hashlib import sha256
from Crypto.Util.number import inverse
from Crypto.Util.Padding import unpad

from tonelli_shanks import tonelli_shanks # To code or use an online version

# from the chall to have the ECC functions --------------------------------------------------
from collections import namedtuple
Point = namedtuple("Point", "x y")
O = 'Origin'

def point_inverse(P: tuple):
    if P == O:
        return P
    return Point(P.x, -P.y % p)

def point_addition(P: tuple, Q: tuple):
    if P == O:
        return Q
    elif Q == O:
        return P
    elif Q == point_inverse(P):
        return O
    else:
        if P == Q:
            aux = ((3*P.x**2 + a) * inverse(2*P.y, p))%p
        else:
            aux = ((Q.y - P.y) * inverse((Q.x - P.x), p))%p
    Rx = (aux**2 - P.x - Q.x) % p
    Ry = (aux*(P.x - Rx) - P.y) % p
    R = Point(Rx, Ry)
    return R

def double_and_add(P: tuple, n: int):
    Q = P
    R = O
    while n > 0:
        if n % 2 == 1:
            R = point_addition(R, Q)
        Q = point_addition(Q, Q)
        n = n // 2
    return R

p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
a = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
b = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
G = Point(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296, 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
# -------------------------------------------------------------------------------------------
# Data from intercepted_message
intercepted_message = open("intercepted_message", 'r').readlines()
pub_key = int(intercepted_message[0][:-1])
computing_time = float(intercepted_message[1].split()[-1][:-8])
iv = bytes.fromhex(intercepted_message[2][:-1])
ciphertext = bytes.fromhex(intercepted_message[3])

# Data from the code
leonard_public_key = 31663442885885219669071274428005652588471134165143253841118506078548146970109
leonard_public_point = Point(leonard_public_key, tonelli_shanks((leonard_public_key**3 + a*leonard_public_key + b)%p,p)[0])
length = 244

# Data from the memory dump
# We notice that bits have been corrupted during the extraction
corrupted_priv_key = "".join(open("memory_dump",'r').readlines()[13:15]).replace('\n','').replace(':','')
corrupted_priv_key = '1' + corrupted_priv_key[-length+1:] # we know the length and starts with a '1'

# Exploiting the given computing time
"""
Looking at the double_and_add function:
    We can see the computed time as the time needed for the point_addition function calls.
    (The time for the loops and affectations is negligible compare to the time needed for the calculations)
    (There is at least a '1' in the binary representation of the private key, so it enters at least once in the if statement)
    When entering the if statement for the first time, the time needed for the point_addition call is negligible (R = O so only a test is carry out)
    At any other moment, point_addition call takes around 30µs (going into the else's segment)
    So the time needed by the double_and_add(P,n) function can be written as:
        T = 30 * (n.bit_length() + n.bit_count() - 1) + 0.05*O(1)
        T = 30 * (n.bit_length() + n.bit_count() - 1)
    We'll call (n.bit_length() + n.bit_count() - 1) the number of operations, which is ~round(T/30):
"""
n_operations = round(computing_time/30)

# Recovering the private key
# Knowing the bit length, one can determine the bit count allowing them to reconstruct the missing bits of the private key.
missing_bits_and_1s = (corrupted_priv_key.count('?'),n_operations-length+1-corrupted_priv_key.count('1'))

def missing_bits(count1, length, res) : # returns the binary representation of numbers with this length and count1 as bit_count()
    assert length > 0
    assert count1 <= length
    if count1 < 1 :
        for bits in res.copy() :
            res.discard(bits)
            res.add(bits.replace('N','0'))
        return res
    if not res :
        res.add('N'*(length))
        return missing_bits(count1, length, res)
    for bits in res.copy() :
        res.discard(bits)
        for k in range(length) :
            if bits[k] == 'N' :
                res.add(bits[:k]+'1'+bits[k+1:])
    return missing_bits(count1-1, length, res)

# Testing all the key possible replacing the '?' by the bits created by the previous function (more info lines 74 and 88)
possible_missing_bits = missing_bits(missing_bits_and_1s[1], missing_bits_and_1s[0], set())
possible_priv_key = list(corrupted_priv_key)
missing_index = [index for index in range(len(corrupted_priv_key)) if corrupted_priv_key[index] == '?']
for bits in possible_missing_bits :
    for i in range(len(missing_index)) :
        possible_priv_key[missing_index[i]] = bits[i]
    key_to_test = int("".join(possible_priv_key),2)
    if double_and_add(G, key_to_test).x == pub_key :
        priv_key = key_to_test
        break

# Deciphering the message
shared_secret_key = double_and_add(leonard_public_point, priv_key).x
derived_aes_key = sha256(str(shared_secret_key).encode('ascii')).digest()
FLAG = unpad(AES.new(derived_aes_key, AES.MODE_CBC, iv).decrypt(ciphertext),16).decode('ascii')
print("dvCTF{"+FLAG+'}')
