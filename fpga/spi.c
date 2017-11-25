// spi.c
// hfang@hmc.edu, mjenrungrot@hmc.edu 24 November 2017
// Send data to hardware accelator using SPI


// Libraries
#include <stdio.h>
#include "EasyPIO.h"


// Constants
#define MSG_PIN 23
#define BLOCK_PIN 24
#define DONE_PIN 25


// Test Cases
// "abc"
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
    char sha256[32];

    pioInit();
    spiInit(244000, 0);

    // Message_load, block_load, and done pins
    pinMode(MSG_PIN, OUTPUT);
    pinMode(BLOCK_PIN, OUTPUT);
    pinMode(DONE_PIN, INPUT);

    // Hardware accelerated encryption
    encrypt(key, sha256);
    printall(key, sha256);
}


//Functions
void printall(char *key, char *sha256){
    printf("Key:         "); printNum(key, 64);
    printf("Sha256:      "); printNum(sha256, 32);
    printf("Expected:    "); printNum(expected, 32);
}

void encrypt(char *key, char *sha256){
    int i;
    int ready;

    digitalWrite(MSG_PIN, 1);
    digitalWrite(BLOCK_PIN, 1);

    for(i = 0; i < 64; i++){
        spiSendReceive(key[i]);
    }

    digitalWrite(BLOCK_PIN, 0);
    digitalWrite(MSG_PIN, 0);

    while (!digitalRead(DONE_PIN));

    for(i=0; i< 32; i++){
        sha256[i] = spiSendReceive(0);
    }

}

void printNum(char *text, int num){
    int i;

    for(i = 0; i < num; i++){
        printf("%02x ", text[i]);
    }
    printf("\n"); 
}


