#ifndef AES_H
#define AES_H

#include <string>
#include <cstring>

using namespace std;

class AES{
    private:
        static const int Nb = 4;  // block size in 32-bit words
        static const int Nk = 8;  // key size in 32-bit words
        static const int Nr = 14; // number of rounds

        static const unsigned int blockSize = 4 * Nb * sizeof(unsigned char);

        void SubBytes(unsigned char **state);
        void InvSubBytes(unsigned char **state);

        unsigned char GetSBox(unsigned char st);
        unsigned char GetInvertSBox(unsigned char st);

        void ShiftRow(unsigned char **state, int i, int p);  // shift row i on p positions
        void ShiftRows(unsigned char **state);
        void InvShiftRows(unsigned char **state);

        void MixColumn(unsigned char **state, int i);
        void MixColumns(unsigned char **state);
        void InvMixColumn(unsigned char **state, int i);
        void InvMixColumns(unsigned char **state);

        void SubWord(unsigned char *word);
        void RotWord(unsigned char *word);

        unsigned char *Xor(unsigned char *a, unsigned char * b, unsigned char *c, unsigned int len);

        void AddRoundKey(unsigned char **state, unsigned char *key);
        void KeyExpansion(unsigned char *key, unsigned char *w); // byte key[4*Nk], word w[Nb*(Nr+1)]

        void Cipher(unsigned char in[], unsigned char out[], unsigned  char key[]); // byte in[4*Nb], byte out[4*Nb], word w[Nb*(Nr+1)
        void InvCipher(unsigned char in[], unsigned char out[], unsigned  char key[]); // byte in[4 * Nb], byte out[4 * Nb], word w[Nb * (Nr+1)]

        unsigned char *PadWithNulls(unsigned char in[], unsigned int inLen, unsigned int new_len);

    public:
        AES();
        unsigned char *EncECB(unsigned char in[], unsigned int inLen, unsigned  char key[], unsigned int &outLen);
        unsigned char *DecECB(unsigned char in[], unsigned int inLen, unsigned  char key[], unsigned int &outLen);
        unsigned char *EncCFB(unsigned char in[], unsigned int inLen, unsigned  char key[], unsigned char * iv, unsigned int &outLen);
        unsigned char *DecCFB(unsigned char in[], unsigned int inLen, unsigned  char key[], unsigned char * iv, unsigned int &outLen);

};

#endif // AES_H
