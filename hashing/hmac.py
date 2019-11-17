from sha2 import sha2 as outer_hash
from sha3 import sha3 as inner_hash

block_size = 64
opad = "".join(chr(x ^ 0x5c) for x in range(block_size))
ipad = "".join(chr(x ^ 0x36) for x in range(block_size))


def hmac(key, msg):

    key_in = key
    key_out = key

    if len(key) > block_size:
        key_in = inner_hash(key)
        key_out = outer_hash(key)

    if len(key) < block_size:
        key_in = key + '0' * (block_size - len(key))
        key_out = key + '0' * (block_size - len(key))

    o_key_pad = key_out.translate(opad)
    i_key_pad = key_in.translate(ipad)

    return outer_hash(o_key_pad + inner_hash(i_key_pad + msg))


if __name__ == "__main__":
    h = hmac("key", "Im ted")
    print(h)
