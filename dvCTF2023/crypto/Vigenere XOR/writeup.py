import string
import math

message_xor = open("message", 'r').read()
assert len(message_xor)//8 == len(message_xor)/8
message_xor = [int(message_xor[k:k+8],2) for k in range(0,len(message_xor),8)]
length = len(message_xor)
dictionnaire = {ord(l) for l in string.printable}

# We testing different key length knowning "dvCTF{" is in the message.
# Testing for key length of {1,2,3,4,5,6} is the same as testing for length of {4,5,6} hence 1|4, 2|4 and 3|6.

def full_key_extend(position : int, key : list[int]) : # key is reused multiple times like with a Vigenere cipher
    start = (key*(math.ceil(position/len(key))))[-position:]
    end = (key*(math.ceil((length-position)/len(key))))[:length-position]
    return start+end

def XOR(known_text : str) :
    known_text = [ord(l) for l in known_text]
    possible_message = set()
    for k in range(length) :
        supposed_key = [l1 ^ l2 for l1,l2 in zip(message_xor[k:],known_text)]
        full_key = full_key_extend(k,supposed_key)
        possible_message.add(tuple(l1 ^ l2 for l1,l2 in zip(message_xor,full_key)))

    print("Possible message with a key of length {}:".format(len(known_text)))
    for m in possible_message :
        if set(m).issubset(dictionnaire) : # message is a text so characters must be printable (\n\r etc... included)
            print("KEY = {} : {}".format("".join(chr(l1 ^ l2) for l1,l2 in zip(m[:len(known_text)],message_xor)), "".join(chr(l) for l in m)))
            FLAG = "".join(chr(l) for l in m)
            print("FLAG = {}".format(FLAG[FLAG.index("dvCTF{"):FLAG.index('}')]))

testing_length_with = ["dvCT", "dvCTF", "dvCTF{"] # Known text respectively of length 4, 5 and 6
for text in testing_length_with :
    XOR(text)
