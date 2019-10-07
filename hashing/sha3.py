from functools import reduce

#########################################################################
#                                                                       #
#                              SHA-3 (256)                              #
#                                                                       #
#########################################################################


DEBUG = False
l = 6
w = 2 ** l

RCi = [
    '0000000000000001', '0000000000008082', '800000000000808A', '8000000080008000',
    '000000000000808B', '0000000080000001', '8000000080008081', '8000000000008009',
    '000000000000008A', '0000000000000088', '0000000080008009', '000000008000000A',
    '000000008000808B', '800000000000008B', '8000000000008089', '8000000000008003',
    '8000000000008002', '8000000000000080', '000000000000800A', '800000008000000A',
    '8000000080008081', '8000000000008080', '0000000080000001', '8000000080008008'
]


def bitstr2str(S):
    return ''.join(["{:02x}".format(int(S[i * 8: (i + 1) * 8][::-1], 2))
                    for i in range(len(S) // 8)])


def string2state(S):
    return [[[int(S[w * (5 * y + x) + z]) for z in range(w)]
             for y in range(5)]
            for x in range(5)]


def state2string(A):
    lanes = [[''.join(['1' if A[i][j][x] else '0' for x in range(w)])
              for j in range(5)]
             for i in range(5)]

    planes = [''.join([lanes[i][j] for i in range(5)])
              for j in range(5)]

    return ''.join([planes[i] for i in range(5)])


def state2d(A):
    lanes = [[''.join(['1' if A[i][j][x] else '0' for x in range(w)])
              for j in range(5)]
             for i in range(5)]
    for i in range(5):
        for j in range(5):
            lanes[i][j] = int(lanes[i][j], 2)
    return lanes


def theta(A):
    """
    Theta Step mapping
    """
    C = [[reduce(lambda i, j: i ^ j, [A[x][y][z] for y in range(5)])
          for z in range(w)]
         for x in range(5)]

    D = [[C[(x - 1) % 5][z] ^ C[(x + 1) % 5][(z - 1) % w] for z in range(w)]
         for x in range(5)]

    A = [[[A[x][y][z] ^ D[x][z] for z in range(w)]
          for y in range(5)]
         for x in range(5)]

    if DEBUG:
        print('after theta: {}'.format(state2d(A)))
    return A


def rho(A):
    """
    rho step mapping - Rotate the bits of each lane by an offset.
    """

    A_ = [[[A[x][y][z] for z in range(w)] for y in range(5)] for x in range(5)]
    for z in range(w):
        A_[0][0][z] = A[0][0][z]
    x, y = 1, 0
    for t in range(24):
        for z in range(w):
            A_[x][y][z] = A[x][y][(z - ((t + 1) * (t + 2)) // 2) % w]
        x, y = y, (2 * x + 3 * y) % 5

    if DEBUG:
        print('after rho: {}'.format(state2d(A_)))
    return A_


def pi(A):
    """
    pi step mapping - Rearrange the positions of the lanes
    """
    A = [[[A[(x + 3 * y) % 5][x][z] for z in range(w)]
          for y in range(5)]
         for x in range(5)]
    if DEBUG:
        print('after pi: {}'.format(state2d(A)))
    return A


def chi(A):
    """
    Chi step mapping - XOR each bit with Non linear operation of two other bits in the same row
    """
    A = [[[A[x][y][z] ^ ((A[(x + 1) % 5][y][z] ^ 1) * A[(x + 2) % 5][y][z])
           for z in range(w)]
          for y in range(5)]
         for x in range(5)]

    if DEBUG:
        print('after chi: {}'.format(state2d(A)))
    return A


def rc(t):
    """
    Round constant for iota step mapping
    """
    if t % 255 == 0:
        return 1
    R = [1, 0, 0, 0, 0, 0, 0, 0]
    for i in range(1, t % 255):
        R = [0] + R
        R[0] = R[0] ^ R[8]
        R[4] = R[4] ^ R[8]
        R[5] = R[5] ^ R[8]
        R[6] = R[6] ^ R[8]
        R = R[:8]
    return R[0]


def iota(A, i):
    """
    Iota step mapping - modify some bits of (0, 0) Lane based on round constant
    """
    A_ = [[[A[x][y][z] for z in range(w)] for y in range(5)] for x in range(5)]

    # 64 bit repr for rc
    RC_bin = "{:064b}".format(int(RCi[i], 16))
    RC = [int(x) for x in RC_bin][::-1]
    for z in range(w):
        A_[0][0][z] = A_[0][0][z] ^ RC[z]

    if DEBUG:
        print('after iota: {}'.format(state2d(A_)))
    return A_


def round(A, i):
    """
    A - state
    i - round index
    """
    return iota(chi(pi(rho(theta(A)))), i)


def keccak_p(S, nr):
    """
    """
    A = string2state(S)
    for i in range(12 + 2 * l - nr, 12 + 2 * l):
        A = round(A, i)
    S = state2string(A)
    return S


def pad(x, m):
    j = (- m - 2) % x
    return '1' + '0' * j + '1'


def sponge(N, r, d, nrounds):
    # absorb
    P = N + pad(r, len(N))
    n = len(P) // r
    c = 2 * d
    b = r + c
    S = '0' * b

    for i in range(n):
        format_spec = "{:0" + str(len(S)) + "b}"
        S_ = format_spec.format(int(S, 2) ^ int(P[i * r:(i + 1) * r] + '0' * c, 2))
        S = keccak_p(S_, nrounds)

    # squeeze
    Z = ''
    while True:
        Z += S[:r]
        if d <= len(Z):
            return Z[:d]
        S = keccak_p(S, nrounds)


def Keccak_c(c, N, d, stateSize, nrounds):
    return sponge(N, stateSize - c, d, nrounds)


def sha3(m):
    state_size = 1600
    nr = 24
    d = 256
    m = ''.join('{0:08b}'.format(ord(x), 'b') for x in m)

    return bitstr2str(Keccak_c(2 * d, m + "01", d, state_size, nr))


if __name__ == '__main__':
    m = 'aaa'
    print("Message: '{}'".format(m))
    print("Digest: {}".format(sha3(m)))