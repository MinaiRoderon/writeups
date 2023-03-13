from PIL import Image
import hashlib
import string

message_image = Image.open("message.png")
(columns, rows) = message_image.size
last_point = eval(open("message",'r').read().split(' : ')[0])
message_hash = open("message",'r').read().split(' : ')[1]

def LSB_from_pixel(point : tuple[int,int]) -> str :
    return "".join((str(val%2) for val in message_image.getpixel(point)[:3]))

authorized_values = set(ord(l) for l in string.ascii_letters + string.digits + '_}{')
def good_24series(serie : tuple[int,int,int]) -> bool :
    if all(val in authorized_values for val in serie) :
        return True
    if serie[0] == 0 and serie[1] == ord('d') and serie[2] == ord('v') :
        return True
    if serie[0] == 0 and serie[1] == 0 and serie[2] == ord('d') :
        return True
    return False

def add_next_point(binaries : set[tuple[str,int]]) -> set[tuple[str,int]] :
    res = binaries.copy()
    for binary,z in binaries :
        next_z = [z-k*100-1 for k in (1,5,10)]
        res.discard((binary,z))
        for zz in next_z :
            res.add((LSB_from_pixel((zz%columns, zz//columns))+LSB_from_pixel(((zz+1)%columns, (zz+1)//columns))+binary, zz))
    return res

def next_3_letters(z:int, end=False) -> set[tuple[tuple[int,int,int],int]] :
    if end :
        possibles = {(LSB_from_pixel(((z-1)%columns, (z-1)//columns))+LSB_from_pixel((z%columns, z//columns)),z-1)}
    else :
        possibles = {("",z)}
    for k in range(4-end) :
        possibles = add_next_point(possibles)
    res = set()
    for binary,z in possibles :
        binary_3 = tuple(int(binary[k:k+8],2) for k in range(0,24,8))
        if good_24series(binary_3) :
            binary_3 = tuple(val for val in binary_3 if val in authorized_values)
            res.add((binary_3,z))
    return res

def soluce() :
    end = tuple(ord(l) for l in "dvCTF{")
    mot_z = next_3_letters(last_point[0] + last_point[1]*columns, True)
    find, res = False, set()
    while not(find) :
        aux = mot_z.copy()
        for m,z in aux :
            mot_z.discard((m,z))
            adding_letters = next_3_letters(z)
            for m2,z2 in adding_letters :
                mot_z.add((m2+m,z2))
                if end == (m2+m)[:6] :
                    find = True
                    res.add("".join(chr(val) for val in m2+m))
    for possible_message in res :
        flag_hash = hashlib.md5()
        flag_hash.update(possible_message.encode())
        if flag_hash.hexdigest() == message_hash :
            return possible_message

print(soluce())
