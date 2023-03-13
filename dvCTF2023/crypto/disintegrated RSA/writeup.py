from Crypto.Util.number import inverse, GCD, long_to_bytes

my_paper = open("my_paper",'r').readlines()
e = int(my_paper[0][:-1][4:])
N = int(my_paper[1][:-1][4:])
message = int(my_paper[2][:-1][10:])
p_modified = my_paper[3][:-2][5:].zfill(2048) # closest usual length
p_modified_int = int(p_modified,2)

# Looking for the couple of bits that has been modified and finding the factorization of N
P2 = [2**k for k in range(len(p_modified))]
P2.reverse()
end = False
for k1 in range(len(p_modified)-1) :
    p_test = p_modified_int + (1 if p_modified[k1]=='0' else -1) * P2[k1]
    for k2 in range(k1+1,len(p_modified)) :
        p_test2 = p_test + (1 if p_modified[k2]=='0' else -1) * P2[k2]
        if N == p_test2*(N//p_test2) :
            p = p_test2
            q = N//p_test2
            end = True
            break
    if end :
        break

assert p*q == N
d = inverse(e,(p-1)*(q-1))

print("dvCTF{" + long_to_bytes(pow(message,d,N)).decode() + '}')
