//
// Herrick Fang, Teerapat Jenrungrot 
// 11/25/2017
// padding.c section 5.1.1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

void padding(char *input, unsigned char* output,  int *len){
    unsigned int inputLength = strlen(input) * 8;
    unsigned int k = findK(inputLength);
    unsigned int outputLength = inputLength  + 1+ k + 64;
    outputLength /= 8;
    printf("inputLength: %d, k: %d, outputLength: %d\n", k, outputLength);
    //output = (unsigned char *)malloc(outputLength * sizeof(unsigned char));
    memset(output, 0, sizeof(output));

    unsigned long long l = 0;
    int i = 0;
    while(input[i] != '\0'){
        output[i] = input[i];
        output[i+1] = 0x80;
        l += 8LL;
        i++;
    }

    printf("l: %lld", l);
    unsigned long long* lengthPosition = (unsigned long long*)(output + ((l + 1 + k) >> 3));
    *lengthPosition = swapBytesOrder(l);
    *len = outputLength;

}

int main()
{ 
  // Add the python message here.
  //  unsigned char msg[2048] = "abc";
  unsigned char msg[2048] = "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu";
  unsigned char output[2048];  
  int paddingLength, i, nblock=0;  
  padding(msg, output, &paddingLength);
  // printf("%s\n",output); 
  printf("Total Length : %d\n", paddingLength);
  for(i=0;i<paddingLength;i++){
    if(i%64 == 0){
        printf("\nBlock %d\n", ++nblock);
    }
    printf("%02x", output[i]);
  }
    

    
  return 0;
}

