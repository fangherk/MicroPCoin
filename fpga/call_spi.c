// spi.c
// hfang@hmc.edu, mjenrungrot@hmc.edu 24 November 2017
// Send data to hardware accelator using SPI


// Libraries
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "EasyPIO.h"

unsigned int findK(unsigned int l){
    return (((448 - l -1) % 512) + 512) % 512;
}

unsigned long long swapBytesOrder(unsigned long long val){
    unsigned long long answer = 0;
    unsigned char buffer[20];
    int i,j;
    for(i=0;i<8;i++){
        buffer[i] = (val & (0xFFULL << (i << 3))) >> (i << 3);
    }
    for(i=7,j=0;i>=0;i--,j++){
        answer |= ((unsigned long long)buffer[i] << (j << 3));
    }
    return answer; 
}

void padding(unsigned char *input, int nBytes, unsigned char* output, int *len){
    unsigned int inputLength = nBytes * 8;
    unsigned int k = findK(inputLength);
    unsigned int outputLength = inputLength  + 1+ k + 64;
    //printf("output length: %d\n", outputLength);
    //printf("input length: %d\n", inputLength);
    outputLength /= 8;
    memset(output, 0, sizeof(output));

    unsigned long long l = 0;
    int i = 0;
    while(i < nBytes){
        output[i] = input[i];
        output[i+1] = 0x80;
        l += 8LL;
        i++;
    }

    unsigned long long* lengthPosition = (unsigned long long*)(output + ((l + 1 + k) >> 3));
    *lengthPosition = swapBytesOrder(l);
    *len = outputLength;

}

unsigned char difficultyBlock[64];

void generateDifficulty(unsigned int arg1){
    // convert bytes order
    unsigned short byte1 = (arg1 & 0xff000000);
    unsigned short byte2 = (arg1 & 0x00ff0000);
    unsigned short byte3 = (arg1 & 0x0000ff00);
    unsigned short byte4 = (arg1 & 0x000000ff);

    unsigned int* diffPosition = (unsigned int*)difficultyBlock;
    *diffPosition = (byte1 >> 24) | (byte2 >> 8) | (byte3 << 8) | (byte4 << 24);
    
}

// Constants
#define MSG_PIN 23
#define BLOCK_PIN 25
#define DONE_PIN 24
#define LOAD_PIN 16
#define INPUT_RDY_PIN 17

// Function prototypes
void encrypt(unsigned char*, unsigned char*);
void printNum(unsigned char*, int);
//void printall(char*, char*);

unsigned char msg[2000000];
unsigned char output[2000000];  
unsigned int arg1;
// Main
int main(int argc, char *argv[]){
    unsigned char key[64];
    memset(msg, 0, sizeof(msg));

    // read bytes
    FILE *fread = fopen("input_message.txt", "rb");
    fseek(fread, 0, SEEK_END);
    int lsize, idxCounter = 0;
    lsize = ftell(fread);
    rewind(fread);
    while(idxCounter < lsize){
        int first = fgetc(fread);
        msg[idxCounter] = (unsigned)first;
    //    printf("%02x", msg[idxCounter]);
        idxCounter++;
    }
    //printf("\n");


    // get difficulty block
    memset(difficultyBlock, 0, sizeof(difficultyBlock));
    arg1 = atoi(argv[1]);
    generateDifficulty(arg1);

    fclose(fread);
    //printf("nBytes = %d\n", lsize);

    int paddingLength, i, nblock=0;  
    padding((unsigned char *)msg, lsize, output, &paddingLength);
    //printNum(output, 192);
    
    int nBlocks = paddingLength / 64;

    int block;
    /*for(block=0; block<nBlocks;block++){
        printf("Block %d\n", block);
        for(i=0;i<64;i++) printf("%02x", output[64*block + i]);
        printf("\n");
    }*/

    pioInit();
    spiInit(6000, 0);
    pinMode(MSG_PIN, OUTPUT);
    pinMode(BLOCK_PIN, OUTPUT);
    pinMode(LOAD_PIN, OUTPUT);
    pinMode(DONE_PIN, INPUT);
    pinMode(INPUT_RDY_PIN, INPUT);

    unsigned char sha256[32];
    unsigned char nonce[4];
    memset(sha256, 0, sizeof(sha256));

        



    for(block=0; block<nBlocks;block++){
        for(i=0;i<64;i++){
            key[i] = output[64*block + i];
      //      fprintf(stderr, "%02x", key[i]);
        }
    //    fprintf(stderr, "\n");
        if(block == 0){
            digitalWrite(MSG_PIN, 1);
            digitalWrite(LOAD_PIN, 1);
        }
        digitalWrite(BLOCK_PIN, 1);
    
        for(i=0; i< 64; i++)  spiSendReceive(key[i]);

        if(block == 0) digitalWrite(LOAD_PIN, 0);           
        digitalWrite(BLOCK_PIN, 0);           
    
        if(block < nBlocks){
            while(!digitalRead(INPUT_RDY_PIN));
        }
    }
//    fprintf(stderr, "Difficulty block\n");
    for(i=0;i<64;i++){
        key[i] = difficultyBlock[i];
  //      fprintf(stderr, "%02x", key[i]);
    }
    digitalWrite(BLOCK_PIN, 1);
    for(i=0; i< 64; i++)  spiSendReceive(key[i]);
    digitalWrite(BLOCK_PIN, 0);           
    digitalWrite(MSG_PIN, 0);

    while (!digitalRead(DONE_PIN));
    for(i=0; i< 32; i++){
        sha256[i] = spiSendReceive(0);
    }
    for(i=0; i<4;i++){
        nonce[i] = spiSendReceive(0);
    }

    int nonceValue = (nonce[0] << 24) | (nonce[1] << 16) | (nonce[2] << 8) | nonce[3];

    FILE *fp = fopen("output.txt", "w");
    fprintf(fp, "%d\n", nonceValue);
    for(i=0; i< 32; i++){
        fprintf(fp, "%02x", sha256[i]);
    }
    fclose(fp);
    //sleep(1);

    // printNum(sha256, 32);
    // printall(key, sha256);
   // printall(key2, sha256);
    return 0;
}


//Functions
void printall(unsigned char *key, unsigned char *sha256){
//    printf("Key:         "); printNum(key, 64);
//    printf("Sha256:      "); printNum(sha256, 32);
//    printf("Expected:    "); printf("11111011011001111000111100110000001111000101111010110100001001111011010010110001100000001010000111111100010100111010111010010001\n");
//    //printNum(expected, 32);
//
//    if(strcmp(expected, sha256) == 0){
//        printf("\nSuccess!\n");
//    }else{
//        printf("\n Test Failed. Saadddd");
//    }
}

void encrypt(unsigned char *key, unsigned char *sha256){
    int i;
    int j = 0;
    int ready;
    for(i = 0; i < 64; i++){
        spiSendReceive(key[i]);
    }
}

void printNum(unsigned char *text, int num){
    int i;

    for(i = 0; i < num; i++){
        // printf("%02x", text[i]);
        printf("%d%d%d%d",(text[i]&8) > 0, (text[i]&4)>0, (text[i]&2)>0, text[i]&1);
    }
    printf("\n"); 
}


