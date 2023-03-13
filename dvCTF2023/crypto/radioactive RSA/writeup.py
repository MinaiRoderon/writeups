from Crypto.Util.number import inverse, long_to_bytes, bytes_to_long
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
import subprocess
import hashlib

# data from the files
message = open("intercepted_message", 'r').readlines()
N = int(message[0][:-1])
e = int(message[1][:-1])
cipher = int(message[2][:-1])
iv, d2_mixed_up_encrypted = message[3][:-1].split(':')
mix_order_length, md5_hash = message[4][:-1].split(':')

memory_file = open("corrupted_memory", 'r').readlines()
d_corrupted_binary = bin(int(''.join(memory_file[10:42]).replace(':','').replace('\n',''),16))[2:]
d_corrupted_binary = d_corrupted_binary.zfill(4096)

higher_bits_range = 4096//2 + e.bit_length() + 1
def closest_d(binary) -> tuple[int, float, int]:
    # return the most probable private key (d), its matching with the faulty d and the k value (e*d = k*phi+1), given in input the faulty d in binary representation
    res = list()
    for k in range(1,e+1) :
        possible_d = bin((k*N)//e)[2:]
        possible_d = '0'*(4096-len(possible_d)) + possible_d
        matching = sum([int(possible_d[k] == binary[k]) for k in range(len(possible_d)-higher_bits_range+1)])/(len(possible_d)-higher_bits_range+1)
        res.append((int(possible_d,2),matching,k))
    res.sort(key=lambda item : item[1], reverse = True)
    return res[0] # First has a matching of 75% and the others are just pseudo random match under 60%

most_probable_d, k = closest_d(d_corrupted_binary)[::2]

"""
Cracking the hash with hashcat (mix_order_length is 11)
    cracking_hash = open("cracking_hash",'w')
    cracking_hash.write(md5_hash+'\n')
    hashcat -m0 -a3 cracking_hash -1 01234567 ?1-?1-?1-?1-?1-?1-?1-?1-?1-?1-?1 -O
gives us:
    70af824c19e86813260c6ed95c021e55:2-0-7-6-4-2-2-5-7-1-3
"""
mix_order = "2-0-7-6-4-2-2-5-7-1-3"

def mix_rewind(order_format : str):
    order = [int(index) for index in order_format.split('-')][::-1]
    return [order[k] for k in range(len(order)) if order[k] not in order[k+1:]]

# reversing the mix and the xor applied on d2, gives the lower bits of d:
d_mixup_order = mix_rewind(mix_order)
derived_aes_key = hashlib.sha256(mix_order.encode('ascii')).digest()
cipher_AES = AES.new(derived_aes_key, AES.MODE_CBC, bytes.fromhex(iv))
d2_mixed_up = bin(bytes_to_long(unpad(cipher_AES.decrypt(bytes.fromhex(d2_mixed_up_encrypted)),16)))[2:].zfill(1600)
d2_mixed_up = [d2_mixed_up[k*len(d2_mixed_up)//8:(k+1)*len(d2_mixed_up)//8] for k in range(8)]
d2 = "".join([d2_mixed_up[index] for index in d_mixup_order])
d_lower_bits = bin(int(d2,2) ^ int(bin(most_probable_d)[2:][::-1],2))[-1600:]

"""
Taking the calculated 1600 lower bits of d in the Coppersmith Algorithm and knowing k too (from the earlier matching), the command:
    python3 partial_d.py 65537 893229405329011031170388407155786874304789238575464954953526102584074064629144436942266669914614851043692328163529510492919136325070634184329207920729828749565245532720326792232560654649632911670832511466959294560397798630151802282028694834358961882940489496898240058093030689588768928370012505691302031212121780810803002573495458802552850834462547639323103297559423179128282514758602133330135253018167111267370377691723405939942315187317893336623023996746106360386889531338893108537091413661478285351412828389683841934570087618048127110368015999494894886692803189318583833641438286553573610826450563738052362949845340681017068756306088958687978242114149403316490950272218659416750151555316596459177988148396419911587861467043140157459376350323678936844540525843452845916790588233078515548428686019504332259346514171531731094264540760166470827311559536760895012372483618905801962881383106768058282744624969801090795353000251617174685339898003590096316096374856729403908694594423741782880254623398883885016406601699118619101516545323025612180762634505074774407780673883353324560217891921506021427879021705886703748315674164243936276187786068758509877764063091378909717370414581109372456634687030746196230257693608341556762845451387593 998935475727213831944554840179414192427575013505549720354696249510751816952372520953679952852407140782377627180954884338672645679234037827023871388051830742155364417592634033798355779789142083115326104608142204802961840037014566245237826769690293827662031124924614491254018766077529190320359908204334773314814343700327071112477518100267729255032900585423424524850825207434672158215800413323567994942025743604954774361892458816752198205006039987764559523964820318750428523990696401 56349
gives us:
    p = 32088482871009956278751271639250175338097763633028977943484619695989123033102642390427275660908105607068285272438039888811487947019822402410872965223312163595541416919101545729043629661218855793273165934603315524800120756981730419835284706175260199450878469717053262543698915734250435241356889203907154048173840131349951012241637003201180230064827081817485604291315255122507172774945355993268704346107305248787035401644405676021333555873546506926666944382389478457228214032880754675793824756387390827897277965925072553077684744505441816208958887925419164167739488338327649876273661364332251928841647785452791491167149
    q = 27836448638585867649333068100942976220006301565052550802379210040385591955450913166644955716335041589477930692821841039905913983491677502230815379048823820975259271042423710540613614205729075317182133409090078279102979304803433246886507780403094972446287307884321778687151801675651684117514721065762193819884770404285365741650070894260909803427262867278099209086434137282938805594183377357642550376846415123004522757116146518193901222573306789348640466055248427879732029357054513870791130512156622426359883881975560311621107561704274687777222149641373852957433784936192604760316525068699329406431884071541679354674957
"""
result = subprocess.Popen(f"python3 partial_d.py 65537 893229405329011031170388407155786874304789238575464954953526102584074064629144436942266669914614851043692328163529510492919136325070634184329207920729828749565245532720326792232560654649632911670832511466959294560397798630151802282028694834358961882940489496898240058093030689588768928370012505691302031212121780810803002573495458802552850834462547639323103297559423179128282514758602133330135253018167111267370377691723405939942315187317893336623023996746106360386889531338893108537091413661478285351412828389683841934570087618048127110368015999494894886692803189318583833641438286553573610826450563738052362949845340681017068756306088958687978242114149403316490950272218659416750151555316596459177988148396419911587861467043140157459376350323678936844540525843452845916790588233078515548428686019504332259346514171531731094264540760166470827311559536760895012372483618905801962881383106768058282744624969801090795353000251617174685339898003590096316096374856729403908694594423741782880254623398883885016406601699118619101516545323025612180762634505074774407780673883353324560217891921506021427879021705886703748315674164243936276187786068758509877764063091378909717370414581109372456634687030746196230257693608341556762845451387593 998935475727213831944554840179414192427575013505549720354696249510751816952372520953679952852407140782377627180954884338672645679234037827023871388051830742155364417592634033798355779789142083115326104608142204802961840037014566245237826769690293827662031124924614491254018766077529190320359908204334773314814343700327071112477518100267729255032900585423424524850825207434672158215800413323567994942025743604954774361892458816752198205006039987764559523964820318750428523990696401 56349".split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
out = result.stdout.read().split('\n')
p = int(out[0][3:])
q = int(out[1][3:])

# deciphering the message:
d = inverse(e,(p-1)*(q-1))
cleartext = long_to_bytes(pow(cipher, d, N)).decode()
# flag with syntax
print("dvCTF{"+cleartext+'}')