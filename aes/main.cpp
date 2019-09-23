#include <iostream>
#include <cassert>
#include <cstring>
#include <cstdio>
#include "aes.h"

using namespace std;

void TestECB(){
    AES aes;

    int plain_len = 16;
    unsigned char plain[plain_len] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
    unsigned char key[] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x011,
    0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f };

    unsigned int padded_len = 0;
    unsigned char *encrypted = aes.EncECB(plain, plain_len * sizeof(unsigned char), key, padded_len);
    unsigned char *decrypted = aes.DecECB(encrypted, plain_len * sizeof(unsigned char), key, padded_len);

    assert(!memcmp(decrypted, plain, 16 * sizeof(unsigned char)));
    cout << "ECB [OK]" << endl;

    delete[] encrypted;
    delete[] decrypted;
}

void TestCFB(){
    AES aes;

    int plain_len = 16;
    unsigned char plain[plain_len] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
    unsigned char iv[plain_len] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
    unsigned char key[] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x011,
    0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f };

    unsigned int padded_len;
    unsigned char *encrypted = aes.EncCFB(plain, plain_len * sizeof(unsigned char), key, iv, padded_len);
    unsigned char *decrypted = aes.DecCFB(encrypted, plain_len * sizeof(unsigned char), key, iv, padded_len);

    assert(!memcmp(decrypted, plain, 16 * sizeof(unsigned char)));
    cout << "CFB [OK]" << endl;

    delete[] encrypted;
    delete[] decrypted;
}

int main()
{
    TestECB();
    TestCFB();
    return 0;
}