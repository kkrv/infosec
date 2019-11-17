WORD_LEN = 32  # in bits
BLOCK_LEN = 64  # in bits
N_ITER = 64  # number of iterations
DEBUG = False

K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

H = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]


def preprocess_message(m):
    l = len(m) * 8 # 8 bit ASCII for each char
    m = ''.join('{0:08b}'.format(ord(x), 'b') for x in m)
    if l % (BLOCK_LEN * 8) != 0:
        k = 0
        while (l + k + BLOCK_LEN + 1) % (BLOCK_LEN * 8) != 0:
            k += 1
        m = m + '1' + k*'0' + '{0:064b}'.format(l)
    if m != '' and DEBUG:
         print(int(m, base=2))
    return m


def rotr(x, n):  # rotate right
    return (x >> n) | (x << (32 - n))


def shr(x, n):  # shift right
    return x >> n


def ch(x, y, z):
    return (x & y) ^ (~x & z)


def maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)


def Sigma0(x):
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22)


def Sigma1(x):
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)


def sigma0(x):
    return rotr(x, 7) ^ rotr(x, 18) ^ shr(x, 3)


def sigma1(x):
    return rotr(x, 17) ^ rotr(x, 19) ^ shr(x, 10)


def generate_words(m):
    w = []
    m_words = split_to_words(m)
    for i in range(0, 16):
        w.append(int(m_words[i], 2))
    for i in range(16, 64):
        w.append((sigma1(w[i - 2]) + w[i - 7] + sigma0(w[i - 15]) + w[i - 16]) % 2 ** 32)
    return w


def split_to_words(m):
    return [m[i: i + WORD_LEN] for i in range(0, len(m), WORD_LEN)]


def split_to_blocks(m):
    return [m[i: i + BLOCK_LEN*8] for i in range(0, len(m), BLOCK_LEN*8)]


def sha2(m):
    m = preprocess_message(m)
    blocks = split_to_blocks(m)

    for block in blocks:
        w = generate_words(block)
        a, b, c, d, e, f, g, h = H.copy()

        if DEBUG:
            print('-----INITIAL-----\na: {}\nb: {}\nc: {}\nd: {}\ne: {}\nf: {}\ng: {}\nh: {}\n'
                  .format(a, b, c, d, e, f, g, h))

        for j in range(N_ITER):
            t1 = h + Sigma1(e) + ch(e, f, g) + K[j] + w[j]
            t2 = Sigma0(a) + maj(a, b, c)
            h = g
            g = f
            f = e
            e = (d + t1) % 2 ** 32
            d = c
            c = b
            b = a
            a = (t1 + t2) % 2 ** 32

            if DEBUG:
                print('ITERATION {}\na: {}\nb: {}\nc: {}\nd: {}\ne: {}\nf: {}\ng: {}\nh: {}\n'
                      .format(j, a, b, c, d, e, f, g, h))

        H[0] = (a + H[0]) % 2 ** 32
        H[1] = (b + H[1]) % 2 ** 32
        H[2] = (c + H[2]) % 2 ** 32
        H[3] = (d + H[3]) % 2 ** 32
        H[4] = (e + H[4]) % 2 ** 32
        H[5] = (f + H[5]) % 2 ** 32
        H[6] = (g + H[6]) % 2 ** 32
        H[7] = (h + H[7]) % 2 ** 32

    result = ""
    for x in H:
        y = format(x, '0x').zfill(8)
        result += y
    return result


if __name__ == '__main__':
    m = ''
    print("Message: '{}'".format(m))
    print('Digest: {}'.format(sha2(m)))