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

void padding(char *input, unsigned char* output, int *len){
    unsigned int inputLength = strlen(input) * 8;
    unsigned int k = findK(inputLength);
    unsigned int outputLength = inputLength  + 1+ k + 64;
    outputLength /= 8;
    memset(output, 0, sizeof(output));

    unsigned long long l = 0;
    int i = 0;
    while(input[i] != '\0'){
        output[i] = input[i];
        output[i+1] = 0x80;
        l += 8LL;
        i++;
    }

    unsigned long long* lengthPosition = (unsigned long long*)(output + ((l + 1 + k) >> 3));
    *lengthPosition = swapBytesOrder(l);
    *len = outputLength;

}


// Constants
#define MSG_PIN 23
#define BLOCK_PIN 25
#define DONE_PIN 24
#define LOAD_PIN 16
#define INPUT_RDY_PIN 17

// Test Cases
// "abc"
char key1[64] = {0x61, 0x62, 0x63, 0x80, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18};

char key2[64] = {0x61, 0x62, 0x63, 0x80, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18};

char key[64] = {0x61, 0x62, 0x63, 0x80, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18};

char expected[32] ={0xBA, 0x78, 0x16, 0xBF, 0x8F, 0x01, 0xCF, 0xEA,
                    0x41, 0x41, 0x40, 0xDE, 0x5D, 0xAE, 0x22, 0x23,  
                    0xB0, 0x03, 0x61, 0xA3, 0x96, 0x17, 0x7A, 0x9C,  
                    0xB4, 0x10, 0xFF, 0x61, 0xF2, 0x00, 0x15, 0xAD};


// Function prototypes
void encrypt(char*, char*);
void printNum(char*, int);
void printall(char*, char*);

// Main
void main(void){
    unsigned char msg[2048] = "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu";
    unsigned char output[2048];  
    int paddingLength, i, nblock=0;  
    padding(msg, output, &paddingLength);
    for(i=0;i<paddingLength;i++){
      if(i < 64) key1[i%64] = output[i];
      else       key2[i%64] = output[i];
    }
    char sha256[32];

    pioInit();
    spiInit(100000, 0);

    delayMicros(1000);
    //printf("slkdjflkf");
    // Message_load, block_load, and done pins
    pinMode(MSG_PIN, OUTPUT);
    pinMode(BLOCK_PIN, OUTPUT);
    pinMode(LOAD_PIN, OUTPUT);
    pinMode(DONE_PIN, INPUT);
    pinMode(INPUT_RDY_PIN, INPUT);

    // Hardware accelerated encryption
  
    digitalWrite(MSG_PIN, 1);
    digitalWrite(BLOCK_PIN, 1);
    digitalWrite(LOAD_PIN, 1);
    for(i=0; i< 64; i++){
        spiSendReceive(key1[i]);
    }
    digitalWrite(LOAD_PIN, 0);
    digitalWrite(BLOCK_PIN, 0);
    while(!digitalRead(INPUT_RDY_PIN));
    digitalWrite(BLOCK_PIN, 1);
    for(i=0;i<64;i++) spiSendReceive(key2[i]);
    digitalWrite(BLOCK_PIN, 0);
    delayMicros(100);
    digitalWrite(MSG_PIN, 0);

    while (!digitalRead(DONE_PIN)){
      //  printf("Waiting1\n");
    };
    delayMicros(100);

    for(i=0; i< 32; i++){
        sha256[i] = spiSendReceive(0);
    }
  
    printall(key, sha256);
   // printall(key2, sha256);
}


//Functions
void printall(char *key, char *sha256){
    printf("Key:         "); printNum(key, 64);
    printf("Sha256:      "); printNum(sha256, 32);
    printf("Expected:    "); printf("11111011011001111000111100110000001111000101111010110100001001111011010010110001100000001010000111111100010100111010111010010001\n");
    //printNum(expected, 32);

    if(strcmp(expected, sha256) == 0){
        printf("\nSuccess!\n");
    }else{
        printf("\n Test Failed. Saadddd");
    }
}

void encrypt(char *key, char *sha256){
    int i;
    int j = 0;
    int ready;
    for(i = 0; i < 64; i++){
        spiSendReceive(key[i]);
    }
}

void printNum(char *text, int num){
    int i;

    for(i = 0; i < num; i++){
        printf("%02x", text[i]);
        //printf("%d%d%d%d",(text[i]&8) > 0, (text[i]&4)>0, (text[i]&2)>0, text[i]&1);
    }
    printf("\n"); 
}


