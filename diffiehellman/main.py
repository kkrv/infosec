import os
import binascii

from hashing.hmac import hmac as mac
from ec.point import Point
from rsassa.pkcs import RSASSA_PKCS as RSA

from Crypto.Cipher import AES


def generate_secret_key(numBits=32):
    return int.from_bytes(os.urandom(numBits // 8), byteorder='big')


def generate_public_key(g: Point, k):
    return g.mul(k)


def pad_pol(p):
    p_str = "{0:b}".format(p.p)
    p_str = '0' * (164 - len(p_str)) + p_str
    return p_str


def pad_point(p: Point):
    x_str = pad_pol(p.x)
    y_str = pad_pol(p.y)
    return x_str + y_str


def sign_point(g: Point, rsa: RSA):
    x_str = pad_pol(g.x)
    y_str = pad_pol(g.y)
    to_sign = x_str + y_str
    return rsa.sign(to_sign)


def sign_points(g1: Point, g2: Point, rsa: RSA):
    to_sign = pad_point(g1) + pad_point(g2)
    return rsa.sign(to_sign)


def encrypt(message, ke):
    lenm = len(message)
    if lenm % 16 != 0:
        message = message + ' ' * (16 - lenm%16)
    obj = AES.new(ke, AES.MODE_ECB)
    return obj.encrypt(message)


def decrypt(ciphertext, ke):
    obj = AES.new(ke, AES.MODE_ECB)
    decr = obj.decrypt(ciphertext)
    return decr.decode('utf-8')


############################################
#                                          #
# SIGMA: Basic Version                     #
#                                          #
############################################

print('-----------------SIGMA: BASIC VERSION-----------------')
g = Point.generate_point()
km = str(generate_secret_key(16))
rsa_b = RSA()
rsa_a = RSA()

aliceSecretKey = generate_secret_key(32)
bobSecretKey = generate_secret_key(32)

aliceId = 'Alice'
bobId = 'Bob'

print('Secret keys are %d, %d' % (aliceSecretKey, bobSecretKey))

# A -> B: g^x
gx = generate_public_key(g, aliceSecretKey)

# B -> A: g^y, B, SIG_B(g^x, g^y), MAC_km(B)
bobCommonKey = gx.mul(bobSecretKey)  # secret value
gy = generate_public_key(g, bobSecretKey)
signed_b = sign_points(gx, gy, rsa_b)
mac_b = mac(km, bobId)

# A -> B: A, SIG_A(g^y, g^x), MAC_km(A)
aliceCommonKey = gy.mul(aliceSecretKey)  # secret value
check_bob_key = rsa_b.verify(signed_b, rsa_b.get_public_key())  # check signed by Bob key
check_bob_id = mac(km, bobId) == mac_b
signed_a = sign_points(gy, gx, rsa_a)
mac_a = mac(km, aliceId)

# check signed by Alice key
check_alice_key = rsa_a.verify(signed_a, rsa_a.get_public_key())
check_alice_id = mac(km, aliceId) == mac_a

print("Bob's common key: {}".format(bobCommonKey))
print("Alice's common key: {}".format(aliceCommonKey))
print("Keys are equal: {}".format(bobCommonKey == aliceCommonKey))
print("Bob's key verification: {}".format(check_bob_key))
print("Alice's key verification: {}".format(check_alice_key))
print("Bob's id verification: {}".format(check_bob_id))
print("Alice's id verification: {}".format(check_alice_id))


################################################
#                                              #
# SIGMA-I: active protection of Initiator’s id #
#                                              #
################################################

print('\n\n----------------SIGMA-I: active protection of Initiator’s id----------------')
g = Point.generate_point()
km = str(generate_secret_key())
ke = os.urandom(16)
rsa_b = RSA()
rsa_a = RSA()

aliceSecretKey = generate_secret_key(32)
bobSecretKey = generate_secret_key(32)

aliceId = 'Alice'
bobId = 'Bob'

print('Secret keys are %d, %d' % (aliceSecretKey, bobSecretKey))

# A -> B: g^x
gx = generate_public_key(g, aliceSecretKey)

# B -> A: g^y, {B, SIG_B(g^x, g^y), MAC_km(B)}_ke
bobCommonKey = gx.mul(bobSecretKey)  # secret value
gy = generate_public_key(g, bobSecretKey)
signed_b = sign_points(gx, gy, rsa_b)
mac_b = mac(km, bobId)
sign_t = signed_b['signature'].hex()
to_encr = bobId + ' ' + signed_b['message'] + ' ' + sign_t + ' ' + mac_b
encr_b = encrypt(to_encr, ke)

# A -> B: {A, SIG_A(g^y, g^x), MAC_km(A)}_ke
aliceCommonKey = gy.mul(aliceSecretKey)  # secret value
bi_retr, signed_b_mes_retr, signed_b_sign_retr, mac_b_retr = decrypt(encr_b, ke).split(' ')[:4]
signed_b_retr = {'message': signed_b_mes_retr, 'signature': bytes.fromhex(signed_b_sign_retr)}
check_bob_key = rsa_b.verify(signed_b_retr, rsa_b.get_public_key())  # check signed by Bob key
check_bob_id = mac(km, bobId) == mac_b_retr
signed_a = sign_points(gy, gx, rsa_a)
mac_a = mac(km, aliceId)
to_encr = aliceId + ' ' + signed_a['message'] + ' ' + signed_a['signature'].hex() + ' ' + mac_a
encr_a = encrypt(to_encr, ke)

# check signed by Alice key
ai_retr, signed_a_mes_retr, signed_a_sign_retr, mac_a_retr = decrypt(encr_a, ke).split(' ')[:4]
signed_a_retr = {'message': signed_a_mes_retr, 'signature': bytes.fromhex(signed_a_sign_retr)}
check_alice_key = rsa_a.verify(signed_a_retr, rsa_a.get_public_key())  # check signed by Bob key
check_alice_id = mac(km, aliceId) == mac_a_retr

print("Bob's common key: {}".format(bobCommonKey))
print("Alice's common key: {}".format(aliceCommonKey))
print("Keys are equal: {}".format(bobCommonKey == aliceCommonKey))
print("Bob's key verification: {}".format(check_bob_key))
print("Alice's key verification: {}".format(check_alice_key))
print("Bob's id verification: {}".format(check_bob_id))
print("Alice's id verification: {}".format(check_alice_id))


##################################################
#                                                #
# SIGMA-R : active protection of Responder’s id  #
#                                                #
##################################################

print('\n\n-----------------SIGMA-R : active protection of Responder’s id----------------')
g = Point.generate_point()
km1 = str(generate_secret_key())
km2 = str(generate_secret_key())
ke1 = os.urandom(16)
ke2 = os.urandom(16)

rsa_b = RSA()
rsa_a = RSA()

aliceSecretKey = generate_secret_key(32)
bobSecretKey = generate_secret_key(32)

aliceId = 'Alice'
bobId = 'Bob'

print('Secret keys are %d, %d' % (aliceSecretKey, bobSecretKey))

# A -> B: g^x
gx = generate_public_key(g, aliceSecretKey)
bobCommonKey = gx.mul(bobSecretKey)  # secret value

# B -> A: g^ y
gy = generate_public_key(g, bobSecretKey)
aliceCommonKey = gy.mul(aliceSecretKey)  # secret value

# A -> B: {A, SIG_A(g^y, g^x), MAC_km1(A)}_ke1
signed_a = sign_points(gy, gx, rsa_a)
mac_a = mac(km1, aliceId)
to_encr = aliceId + ' ' + signed_a['message'] + ' ' + signed_a['signature'].hex() + ' ' + mac_a
encr_a = encrypt(to_encr, ke1)

# B -> A: {B, SIG_B(g^x, g^y), MAC_km(A)}_ke
ai_retr, signed_a_mes_retr, signed_a_sign_retr, mac_a_retr = decrypt(encr_a, ke1).split(' ')[:4]
signed_a_retr = {'message': signed_a_mes_retr, 'signature': bytes.fromhex(signed_a_sign_retr)}
check_alice_key = rsa_a.verify(signed_a_retr, rsa_a.get_public_key())  # check signed by Bob key
check_alice_id = mac(km1, aliceId) == mac_a_retr

signed_b = sign_points(gx, gy, rsa_b)
mac_b = mac(km2, bobId)
to_encr = bobId + ' ' + signed_b['message'] + ' ' + signed_b['signature'].hex() + ' ' + mac_b
encr_b = encrypt(to_encr, ke2)

# check signed by Alice key
bi_retr, signed_b_mes_retr, signed_b_sign_retr, mac_b_retr = decrypt(encr_b, ke2).split(' ')[:4]
signed_b_retr = {'message': signed_b_mes_retr, 'signature': bytes.fromhex(signed_b_sign_retr)}
check_bob_key = rsa_b.verify(signed_b_retr, rsa_b.get_public_key())  # check signed by Bob key
check_bob_id = mac(km2, bobId) == mac_b_retr

print("Bob's common key: {}".format(bobCommonKey))
print("Alice's common key: {}".format(aliceCommonKey))
print("Keys are equal: {}".format(bobCommonKey == aliceCommonKey))
print("Bob's key verification: {}".format(check_bob_key))
print("Alice's key verification: {}".format(check_alice_key))
print("Bob's id verification: {}".format(check_bob_id))
print("Alice's id verification: {}".format(check_alice_id))
