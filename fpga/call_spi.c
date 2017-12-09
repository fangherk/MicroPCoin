// spi.c
// hfang@hmc.edu, mjenrungrot@hmc.edu 8 December 2017
// Send data to hardware accelator using SPI

// Libraries
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "EasyPIO.h"

// Find k
unsigned int findK(unsigned int l){
    return (((448 - l -1) % 512) + 512) % 512;
}

// Swap Big + Little Endian
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

// Pad a given input to create input_message
void padding(unsigned char *input, int nBytes, unsigned char* output, int *len){
    unsigned int inputLength = nBytes * 8;
    unsigned int k = findK(inputLength);
    unsigned int outputLength = inputLength  + 1+ k + 64;

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

// Generate the difficulty from the terminal input
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
unsigned char msg[2000000];
unsigned char output[2000000];  
unsigned int arg1;


// Main
int main(int argc, char *argv[]){

    // Create a place to store each block   
    unsigned char key[64];

    // Prepare the message by setting it to 0s
    memset(msg, 0, sizeof(msg));

    // Read the input message through a text file
    FILE *fread = fopen("input_message.txt", "rb");
    fseek(fread, 0, SEEK_END);


    // Start the counter and sizes
    int lsize, idxCounter = 0;
    lsize = ftell(fread);
    rewind(fread);


    // Wait for the counter to be less than the size
    while(idxCounter < lsize){
        int first = fgetc(fread);
        msg[idxCounter] = (unsigned)first;
        idxCounter++;
    }


    // Generate a difficulty block to send to the FPGA
    memset(difficultyBlock, 0, sizeof(difficultyBlock));
    arg1 = atoi(argv[1]);
    generateDifficulty(arg1);

    fclose(fread);

    // Pad the message according to FIPS
    int paddingLength, i, nblock=0;  
    padding((unsigned char *)msg, lsize, output, &paddingLength);
    int nBlocks = paddingLength / 64;
    int block;

    // Initialize pins for blocks
    pioInit();
    spiInit(150000, 0);
    pinMode(MSG_PIN, OUTPUT);
    pinMode(BLOCK_PIN, OUTPUT);
    pinMode(LOAD_PIN, OUTPUT);
    pinMode(DONE_PIN, INPUT);
    pinMode(INPUT_RDY_PIN, INPUT);

    unsigned char sha256[32];
    unsigned char nonce[4];
    memset(sha256, 0, sizeof(sha256));


    // Start the block sending process. 
    // Start with high message and load pins.
    // Turn off the load pin and continue after the
    // first couple blocks. Continue sending blocks
    // and sending on/off signals accordingly.   

    for(block=0; block<nBlocks;block++){
        for(i=0;i<64;i++){
            key[i] = output[64*block + i];
        }
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

    // Send the last difficulty block
    for(i=0;i<64;i++){
        key[i] = difficultyBlock[i];
    }
    digitalWrite(BLOCK_PIN, 1);
    for(i=0; i< 64; i++)  spiSendReceive(key[i]);
    digitalWrite(BLOCK_PIN, 0);           
    digitalWrite(MSG_PIN, 0);

    // End the output and wait for the response from the FPGA
    while (!digitalRead(DONE_PIN));

    // Get the Sha256 output hash
    for(i=0; i< 32; i++){
        sha256[i] = spiSendReceive(0);
    }

    // Get the nonce value
    for(i=0; i<4;i++){
        nonce[i] = spiSendReceive(0);
    }

    // Parse the nonce vlaue and output to a file, then output the sha256 value
    int nonceValue = (nonce[0] << 24) | (nonce[1] << 16) | (nonce[2] << 8) | nonce[3];

    FILE *fp = fopen("output.txt", "w");
    fprintf(fp, "%d\n", nonceValue);
    for(i=0; i< 32; i++){
        fprintf(fp, "%02x", sha256[i]);
    }
    fclose(fp);
    return 0;
}



